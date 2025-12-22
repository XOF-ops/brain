import os
import sys
import pytest
from unittest.mock import patch, Mock

# Ensure project root is on sys.path so tests can import the webhook package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from webhook.master_brain_webhook import app
from requests import Timeout

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_missing_text(client):
    with patch.object(app, 'logger') as mock_logger:
        res = client.post('/webhook/master-brain', json={})
        assert res.status_code == 400
        mock_logger.warning.assert_called_with("Missing 'text' field in request")


def test_health(client):
    res = client.get('/health')
    assert res.status_code == 200
    body = res.get_json()
    assert body['status'] == 'ONLINE'
    assert 'forwarding_to' in body


def test_scan_forward_success(client):
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {'match': 'P119'}

    with patch('webhook.master_brain_webhook.requests.post', return_value=mock_resp) as mock_post:
        with patch.object(app, 'logger') as mock_logger:
            res = client.post('/webhook/master-brain', json={'text': 'I want freedom but fear isolation'})
            assert res.status_code == 200
            assert res.get_json() == {'match': 'P119'}
            mock_post.assert_called_once()
            # Ensure we logged forwarding and response
            mock_logger.info.assert_any_call("Forwarding scan request", extra={'payload': {'text': 'I want freedom but fear isolation', 'rate_limited': False}})
            mock_logger.info.assert_any_call("Received response from Master Brain", extra={'status': 200, 'body': {'match': 'P119'}})


def test_master_brain_timeout(client):
    with patch('webhook.master_brain_webhook.requests.post', side_effect=Timeout('t')):
        res = client.post('/webhook/master-brain', json={'text': 'x'})
        assert res.status_code == 504
        assert 'Timeout contacting Master Brain' in res.get_json().get('error', '')


def test_invalid_json_from_master_brain(client):
    mock_resp = Mock()
    mock_resp.status_code = 502
    mock_resp.text = 'not json'
    mock_resp.json.side_effect = ValueError()

    with patch('webhook.master_brain_webhook.requests.post', return_value=mock_resp):
        with patch.object(app, 'logger') as mock_logger:
            res = client.post('/webhook/master-brain', json={'text': 'I want freedom'})
            assert res.status_code == 502
            body = res.get_json()
            assert body['error'] == 'Invalid JSON from Master Brain'
            assert body['raw'] == 'not json'
            mock_logger.error.assert_called_with("Invalid JSON from Master Brain", extra={'raw': 'not json'})
