import os
import sys
import json
import pytest
from unittest.mock import patch, Mock

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.api import app
from subprocess import TimeoutExpired

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_missing_proposal(client):
    res = client.post('/amend', json={})
    assert res.status_code == 400


def test_unauthorized(client):
    res = client.post('/amend', json={'proposal': 'A12: x'})
    assert res.status_code == 403


def test_amend_success(client, monkeypatch):
    # Mock subprocess.run to return a successful JSON on stdout
    mock_proc = Mock()
    mock_proc.returncode = 0
    mock_proc.stdout = json.dumps({'status': 'accepted'})

    with patch('engine.api.subprocess.run', return_value=mock_proc) as mock_run:
        headers = {'Authorization': f"Bearer {os.environ.get('ARCHITECT_KEY', 'ARCHITECT_KEY')}"}
        res = client.post('/amend', json={'proposal': 'A12: Flow must scale'}, headers=headers)
        assert res.status_code == 200
        assert res.get_json() == {'status': 'accepted'}
        mock_run.assert_called_once()


def test_engine_nonzero_exit(client):
    mock_proc = Mock()
    mock_proc.returncode = 1
    mock_proc.stdout = ''
    mock_proc.stderr = 'something bad'

    with patch('engine.api.subprocess.run', return_value=mock_proc):
        headers = {'Authorization': f"Bearer {os.environ.get('ARCHITECT_KEY', 'ARCHITECT_KEY')}"}
        res = client.post('/amend', json={'proposal': 'A12: Flow must scale'}, headers=headers)
        assert res.status_code == 500
        assert 'error' in res.get_json()


def test_engine_timeout(client):
    with patch('engine.api.subprocess.run', side_effect=TimeoutExpired(cmd=['x'], timeout=1)):
        headers = {'Authorization': f"Bearer {os.environ.get('ARCHITECT_KEY', 'ARCHITECT_KEY')}"}
        res = client.post('/amend', json={'proposal': 'A12: Flow must scale'}, headers=headers)
        assert res.status_code == 504
        assert 'Engine timeout' in res.get_json().get('error', '')
