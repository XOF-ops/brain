#!/usr/bin/env python3
"""Master Brain Engine API (Amendment Flow)

Start with:

  pip install flask
  python3 engine/api.py

The API expects the Architect Key in an Authorization header:
  Authorization: Bearer <key>

POST /amend JSON: { "proposal": "A12: Flow must scale with friction" }
"""
from flask import Flask, request, jsonify
import os
import sys
import subprocess
import json
from typing import Any, Tuple

app = Flask(__name__)

ENGINE_PATH = os.path.join(os.path.dirname(__file__), 'master_brain.py')
PYTHON_EXEC = sys.executable if 'sys' in locals() else 'python3'
ARCHITECT_KEY = os.environ.get('ARCHITECT_KEY', 'ARCHITECT_KEY')
ENGINE_TIMEOUT = int(os.environ.get('ENGINE_TIMEOUT', '10'))


def run_engine(args, timeout: int = ENGINE_TIMEOUT) -> Tuple[Any, int]:
    cmd = [PYTHON_EXEC, ENGINE_PATH] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        return {"error": "Engine timeout", "details": str(e)}, 504
    except Exception as e:
        return {"error": "Engine execution error", "details": str(e)}, 500

    if result.returncode != 0:
        try:
            if result.stdout:
                payload = json.loads(result.stdout)
                # Ensure there's an error key for consistency
                payload.setdefault('error', 'Engine exited with non-zero status')
            else:
                payload = {"error": "Engine exited with non-zero status", "stderr": result.stderr}
        except Exception:
            payload = {
                "error": "Engine exited with non-zero status",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        return payload, 500

    try:
        return json.loads(result.stdout), 200
    except json.JSONDecodeError:
        return {"error": "Invalid JSON output from engine", "raw_stdout": result.stdout}, 500


@app.route('/amend', methods=['POST'])
def amend():
    data = request.get_json(silent=True)
    if not data or 'proposal' not in data:
        return jsonify({"error": "Missing 'proposal' field"}), 400

    auth_header = request.headers.get('Authorization')
    expected = f"Bearer {ARCHITECT_KEY}"
    if auth_header != expected:
        return jsonify({"error": "Unauthorized. Governance requires the Architect's Key."}), 403

    args = ['--amend', data['proposal']]
    response, status = run_engine(args)
    return jsonify(response), status


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ONLINE", "system": "MASTER_BRAIN_API", "version": "11.4"}), 200


if __name__ == '__main__':
    print('>> MASTER_BRAIN API (Engine) LISTENING ON PORT 5000...')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '5000')))
