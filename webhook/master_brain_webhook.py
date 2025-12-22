#!/usr/bin/env python3
"""Simple webhook that forwards requests to the Master Brain /scan endpoint.

Usage:
  MASTER_BRAIN_URL="http://localhost:5000" PORT=8080 python webhook/master_brain_webhook.py

The webhook expects JSON: { "text": "...", "rate_limited": false }
It forwards that payload to ${MASTER_BRAIN_URL}/scan and returns the response unchanged.
"""
from flask import Flask, request, jsonify
import os
import requests
import logging

app = Flask(__name__)

# Configurable via environment
MASTER_BRAIN_URL = os.environ.get("MASTER_BRAIN_URL", "http://localhost:80")
TIMEOUT = int(os.environ.get("MASTER_BRAIN_TIMEOUT", "10"))
LOG_LEVEL = os.environ.get("MASTER_BRAIN_LOG_LEVEL", "INFO")
# Enable dev auto-reload when DEV_AUTO_RELOAD=1
app.config['DEBUG'] = os.environ.get('DEV_AUTO_RELOAD', '0') == '1'

# Configure logger
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
logger = logging.getLogger('master_brain_webhook')
logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
if not logger.handlers:
    logger.addHandler(handler)
app.logger = logger


@app.route("/webhook/master-brain", methods=["POST"])
def master_brain_webhook():
    data = request.get_json(silent=True)
    if not data or 'text' not in data:
        app.logger.warning("Missing 'text' field in request")
        return jsonify({'error': "Missing 'text' field"}), 400

    payload = {
        'text': data['text'],
        'rate_limited': bool(data.get('rate_limited', False))
    }

    app.logger.info("Forwarding scan request", extra={"payload": payload})
    try:
        resp = requests.post(f"{MASTER_BRAIN_URL.rstrip('/')}/scan", json=payload, timeout=TIMEOUT)
    except requests.Timeout as e:
        app.logger.error("Timeout contacting Master Brain", exc_info=e)
        return jsonify({'error': 'Timeout contacting Master Brain', 'details': str(e)}), 504
    except requests.RequestException as e:
        app.logger.error("Error contacting Master Brain", exc_info=e)
        return jsonify({'error': 'Error contacting Master Brain', 'details': str(e)}), 502

    # Try to return JSON body from Master Brain verbatim, fallback to raw text
    try:
        body = resp.json()
        app.logger.info("Received response from Master Brain", extra={"status": resp.status_code, "body": body})
        return jsonify(body), resp.status_code
    except ValueError:
        app.logger.error("Invalid JSON from Master Brain", extra={"raw": resp.text})
        return jsonify({'error': 'Invalid JSON from Master Brain', 'raw': resp.text}), 502


@app.route('/health', methods=['GET'])
def health():
    """Simple health endpoint for monitoring"""
    return jsonify({
        'status': 'ONLINE',
        'service': 'MASTER_BRAIN_WEBHOOK',
        'forwarding_to': MASTER_BRAIN_URL,
        'debug': app.config['DEBUG']
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8080'))
    app.logger.info(f"MASTER_BRAIN WEBHOOK LISTENING ON PORT {port}... (forwarding to {MASTER_BRAIN_URL})")
    # Use Flask's built-in reloader when debug is enabled
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])