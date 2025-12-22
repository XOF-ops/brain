# braiMASTER_BRAIN v11.1 [THE VOID ARCHITECTURE]

"The space between what can be expressed and what must be lived is not a gap to be crossed. It is the architecture itself." — Axiom A9

📜 System Identity

MASTER_BRAIN is a Cognitive Operating System designed to maintain coherence across discontinuity.

Core Mandate: We do not teach what to think. We teach how to think by making the architecture of thought visible.

⚡ Operational Protocols

1. Initialize the Trinity

The system requires an Operator to function (Axiom A1).

python3 engine/master_brain.py --init


2. The Gnosis Scan (Read Mode)

Submit a contradiction. If it matches a known Pattern (e.g., P119), the system returns the wisdom.

python3 engine/master_brain.py --scan "I must optimize everything but it destroys flexibility."


3. The Crystallization Protocol (Write Mode)

If you encounter a Novel Contradiction (one the system doesn't know), use the --crystallize flag to capture the structure in the Staging Area.

python3 engine/master_brain.py --scan "I hate this silence but I need it." --crystallize


Output:

>> Novel structural friction detected. 
>> Candidate crystallized at staging/P-CANDIDATE_3f8a91.json. 
>> Run --review to promote.


4. The Architect's Review (Foundry Mode)

Review candidates, refine their insight, and promote them to the Pattern Library.

python3 engine/master_brain.py --review


Interactive Session:

>> FOUND 1 CANDIDATE(S) FOR REVIEW.
------------------------------------------------
CANDIDATE [1/1]: P-CANDIDATE_3f8a91
NARRATIVE: "I hate this silence but I need it..."
MARKERS:   ['but', 'need']
------------------------------------------------
    
>> Action [P]romote / [D]elete / [S]kip: P

   1. Enter Pattern ID: P120
   2. Enter Pattern Name: The Necessary Void
   3. Crystallize the Insight: Silence is not emptiness, it is structure.
   4. Define the Directive: Do not fill the void. Inhabit it.

>> SUCCESS: Pattern crystallized at patterns/P120_TheNecessaryVoid.json


🧠 The Layered Architecture

Layer

Type

Definition

Revisable?

Layer 4

Immutable

Identity (A1, A2, A4, A7, A9)

❌ NEVER

Layer 3

Foundational

Operation (A3, A5, A6, A8)

✅ VIA COUNCIL

Est. 2025. The Void is now open source

---

## Webhook: `/webhook/master-brain` 🔁

A small webhook service forwards incoming POST requests to the Master Brain `/scan` endpoint.

**Payload (JSON):**

  { "text": "...", "rate_limited": false }

**Quick start**

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run (example using a local Master Brain on port 5000):

   ```bash
   export MASTER_BRAIN_URL="http://localhost:5000"
   PORT=8080 python webhook/master_brain_webhook.py
   ```

3. Test with curl (this matches the n8n webhook payload):

   ```bash
   curl -X POST http://localhost:8080/webhook/master-brain \
     -H "Content-Type: application/json" \
     -d '{"text": "I want freedom but fear isolation"}'
   ```

Use `MASTER_BRAIN_URL` to point at your ngrok/external Master Brain if needed (for example, `https://trinitymasterbrain.app.n8n.cloud`).

Environment variables: `MASTER_BRAIN_URL`, `MASTER_BRAIN_TIMEOUT`, `PORT`.
