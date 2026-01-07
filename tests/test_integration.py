"""Integration tests for the Brain system.

These tests validate the Brain API and webhook against test conversation data
from the XOF-ops/test repository. They test end-to-end flows including:
- Pattern detection validation
- Webhook forwarding behavior
- API response formats
"""
import os
import sys
import json
import pytest
from unittest.mock import patch, Mock

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from webhook.master_brain_webhook import app as webhook_app
from engine.api import app as api_app


# Sample test data based on XOF-ops/test chat_conversations
INTEGRATION_TEST_DATA = {
    "id": "integration-test-001",
    "metadata": {
        "patterns_detected": [
            {
                "message_index": 0,
                "pattern": {
                    "pattern_id": "P119",
                    "insight": "Detected P119 pattern (mock mode)",
                    "match_score": 0.75,
                    "mock": True
                }
            }
        ],
        "model": "mistralai/mistral-7b-instruct:free"
    },
    "messages": [
        {
            "role": "user",
            "content": "I need to optimize my workflow but it kills creativity"
        }
    ]
}

N8N_INTEGRATION_TEST_DATA = {
    "id": "n8n-integration-test",
    "metadata": {
        "patterns_detected": [
            {
                "message_index": 0,
                "pattern": {
                    "engine": "MASTER_BRAIN",
                    "version": "1.0",
                    "axioms_detected": ["A1", "A2", "A4", "A9"],
                    "patterns_detected": ["P001"],
                    "coherence": {"score": "4/5", "coherent": True},
                    "classification": "MASTER_BRAIN",
                    "pattern_id": "P001",
                    "pattern_name": "Dyadic Synthesis",
                    "match_score": 0.85
                }
            }
        ]
    },
    "messages": [
        {
            "role": "user",
            "content": "The dialogue between us creates relational knowledge."
        }
    ]
}

HEARTBEAT_TEST_DATA = {
    "id": "heartbeat",
    "messages": [
        {"role": "user", "content": "ping"},
        {"role": "assistant", "content": " [/s] "}
    ]
}


@pytest.fixture
def webhook_client():
    """Fixture for webhook test client."""
    with webhook_app.test_client() as client:
        yield client


@pytest.fixture
def api_client():
    """Fixture for API test client."""
    with api_app.test_client() as client:
        yield client


class TestWebhookIntegration:
    """Integration tests for the Master Brain webhook."""

    def test_pattern_detection_forwarding(self, webhook_client):
        """Test that pattern detection requests are properly forwarded."""
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "pattern_id": "P119",
            "match_score": 0.75,
            "insight": "Detected P119 pattern"
        }

        with patch('webhook.master_brain_webhook.requests.post', return_value=mock_resp):
            # Use test data from XOF-ops/test
            text = INTEGRATION_TEST_DATA["messages"][0]["content"]
            res = webhook_client.post(
                '/webhook/master-brain',
                json={'text': text}
            )

            assert res.status_code == 200
            body = res.get_json()
            assert body["pattern_id"] == "P119"
            assert body["match_score"] == 0.75

    def test_dyadic_synthesis_pattern(self, webhook_client):
        """Test P001 Dyadic Synthesis pattern detection."""
        mock_resp = Mock()
        mock_resp.status_code = 200
        expected_pattern = N8N_INTEGRATION_TEST_DATA["metadata"]["patterns_detected"][0]["pattern"]
        mock_resp.json.return_value = expected_pattern

        with patch('webhook.master_brain_webhook.requests.post', return_value=mock_resp):
            text = N8N_INTEGRATION_TEST_DATA["messages"][0]["content"]
            res = webhook_client.post(
                '/webhook/master-brain',
                json={'text': text}
            )

            assert res.status_code == 200
            body = res.get_json()
            assert body["pattern_id"] == "P001"
            assert body["pattern_name"] == "Dyadic Synthesis"
            assert body["match_score"] == 0.85
            assert body["coherence"]["coherent"] is True
            assert "A1" in body["axioms_detected"]

    def test_heartbeat_message(self, webhook_client):
        """Test simple heartbeat/ping messages are forwarded."""
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"status": "pong", "service": "MASTER_BRAIN"}

        with patch('webhook.master_brain_webhook.requests.post', return_value=mock_resp):
            text = HEARTBEAT_TEST_DATA["messages"][0]["content"]
            res = webhook_client.post(
                '/webhook/master-brain',
                json={'text': text}
            )

            assert res.status_code == 200
            body = res.get_json()
            assert body["status"] == "pong"

    def test_rate_limited_flag(self, webhook_client):
        """Test that rate_limited flag is properly forwarded."""
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"processed": True}

        with patch('webhook.master_brain_webhook.requests.post', return_value=mock_resp) as mock_post:
            res = webhook_client.post(
                '/webhook/master-brain',
                json={'text': 'test message', 'rate_limited': True}
            )

            assert res.status_code == 200
            # Verify that rate_limited was included in the forwarded payload
            call_args = mock_post.call_args
            forwarded_payload = call_args.kwargs['json']
            assert forwarded_payload['rate_limited'] is True


class TestAPIIntegration:
    """Integration tests for the Brain API."""

    def test_amend_proposal_format(self, api_client):
        """Test that proposals follow the expected format (A<num>: <text>)."""
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_proc.stdout = json.dumps({
            'status': 'accepted',
            'amendment': 'A12',
            'result': 'Layer 3 updated'
        })

        with patch('engine.api.subprocess.run', return_value=mock_proc):
            headers = {'Authorization': f"Bearer {os.environ.get('ARCHITECT_KEY', 'ARCHITECT_KEY')}"}
            res = api_client.post(
                '/amend',
                json={'proposal': 'A12: Flow must scale with friction'},
                headers=headers
            )

            assert res.status_code == 200
            body = res.get_json()
            assert body['status'] == 'accepted'
            assert body['amendment'] == 'A12'

    def test_api_health_endpoint(self, api_client):
        """Test the API health endpoint returns expected format."""
        res = api_client.get('/health')

        assert res.status_code == 200
        body = res.get_json()
        assert body['status'] == 'ONLINE'
        assert body['system'] == 'MASTER_BRAIN_API'
        assert 'version' in body

    def test_pattern_based_amendment(self, api_client):
        """Test amendment based on detected pattern."""
        # Simulate a pattern detection triggering an amendment
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_proc.stdout = json.dumps({
            'status': 'accepted',
            'triggered_by': 'P119',
            'amendment': 'A13'
        })

        with patch('engine.api.subprocess.run', return_value=mock_proc):
            headers = {'Authorization': f"Bearer {os.environ.get('ARCHITECT_KEY', 'ARCHITECT_KEY')}"}
            # Proposal based on P119 Optimization Paradox pattern
            res = api_client.post(
                '/amend',
                json={'proposal': 'A13: Balance optimization with creative flexibility'},
                headers=headers
            )

            assert res.status_code == 200
            body = res.get_json()
            assert body['status'] == 'accepted'


class TestConversationDataValidation:
    """Tests validating the structure of conversation test data."""

    def test_integration_data_structure(self):
        """Validate that integration test data has required fields."""
        assert 'id' in INTEGRATION_TEST_DATA
        assert 'messages' in INTEGRATION_TEST_DATA
        assert 'metadata' in INTEGRATION_TEST_DATA
        assert len(INTEGRATION_TEST_DATA['messages']) > 0
        assert 'content' in INTEGRATION_TEST_DATA['messages'][0]
        assert 'role' in INTEGRATION_TEST_DATA['messages'][0]

    def test_pattern_metadata_structure(self):
        """Validate pattern metadata follows expected schema."""
        patterns = INTEGRATION_TEST_DATA['metadata']['patterns_detected']
        assert len(patterns) > 0

        pattern = patterns[0]['pattern']
        assert 'pattern_id' in pattern
        assert 'match_score' in pattern
        assert isinstance(pattern['match_score'], (int, float))
        assert 0 <= pattern['match_score'] <= 1

    def test_n8n_pattern_structure(self):
        """Validate n8n integration test data structure."""
        patterns = N8N_INTEGRATION_TEST_DATA['metadata']['patterns_detected']
        pattern = patterns[0]['pattern']

        # Verify n8n specific fields
        assert 'engine' in pattern
        assert pattern['engine'] == 'MASTER_BRAIN'
        assert 'version' in pattern
        assert 'axioms_detected' in pattern
        assert 'coherence' in pattern
        assert 'score' in pattern['coherence']
        assert 'coherent' in pattern['coherence']

    def test_message_roles(self):
        """Validate that messages have valid roles."""
        valid_roles = {'user', 'assistant', 'system'}

        for msg in HEARTBEAT_TEST_DATA['messages']:
            assert msg['role'] in valid_roles
