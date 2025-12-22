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

app = Flask(__name__)

# Configurable via environment
MASTER_BRAIN_URL = os.environ.get("MASTER_BRAIN_URL", "http://localhost:80")
TIMEOUT = int(os.environ.get("MASTER_BRAIN_TIMEOUT", "10"))


@app.route("/webhook/master-brain", methods=["POST"])
def master_brain_webhook():
    data = request.get_json(silent=True)
    if not data or 'text' not in data:
        return jsonify({'error': "Missing 'text' field"}), 400

    payload = {
        'text': data['text'],
        'rate_limited': bool(data.get('rate_limited', False))
    }

    try:
        resp = requests.post(f"{MASTER_BRAIN_URL.rstrip('/')}/scan", json=payload, timeout=TIMEOUT)
    except requests.Timeout as e:
        return jsonify({'error': 'Timeout contacting Master Brain', 'details': str(e)}), 504
    except requests.RequestException as e:
        return jsonify({'error': 'Error contacting Master Brain', 'details': str(e)}), 502

    # Try to return JSON body from Master Brain verbatim, fallback to raw text
    try:
        return jsonify(resp.json()), resp.status_code
    except ValueError:
        return jsonify({'error': 'Invalid JSON from Master Brain', 'raw': resp.text}), 502


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8080'))
    print(f">> MASTER_BRAIN WEBHOOK LISTENING ON PORT {port}... (forwarding to {MASTER_BRAIN_URL})")
    app.run(host='0.0.0.0', port=port)
