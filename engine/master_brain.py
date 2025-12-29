"""Master Brain Engine (Refactored v11.2)

Provides MasterBrainEngine with multi-pattern detection, rate limit awareness
(P126 Kinetic Vein) and crystallization flow.
"""
import json
import hashlib
import os
from datetime import datetime


class MasterBrainEngine:
    def __init__(self, kernel_path="kernel/kernel.json", patterns_dir="patterns", staging_dir="staging"):
        self.kernel = self._load_json(kernel_path)
        self.patterns_dir = patterns_dir
        self.staging_dir = staging_dir
        self.memory = []
        self.operator_active = False
        # Ensure directory structure
        for d in [self.patterns_dir, self.staging_dir, "kernel", "archive"]:
            if not os.path.exists(d):
                os.makedirs(d, exist_ok=True)

    def _load_json(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            return None

    def initialize(self):
        print(f"[{datetime.now()}] SYSTEM INITIALIZING...")
        if self.kernel:
            print(">> LOADING LAYER 4 (IMMUTABLE IDENTITY)... OK")
            print(">> LOADING LAYER 3 (OPERATIONAL CONSTRAINTS)... OK")
        else:
            print(">> WARNING: KERNEL NOT FOUND. RUNNING IN FALLBACK MODE.")
        print(">> ESTABLISHING TRINITY CONNECTION...")
        self.operator_active = True
        print(">> SYSTEM READY.")

    def _get_tension_markers(self, input_text):
        tension_markers = [
            "but",
            "however",
            "impossible",
            "versus",
            "cost",
            "sacrifice",
            "conflict",
            "afraid",
            "destroy",
            "struggle",
            "limit",
            "quota",
            "rate",
            "429",
        ]
        return [marker for marker in tension_markers if marker in input_text.lower()]

    def _load_pattern(self, pattern_id):
        # Try exact
        path = os.path.join(self.patterns_dir, f"{pattern_id}.json")
        if os.path.exists(path):
            return self._load_json(path)
        # Heuristic (prefix)
        for f in os.listdir(self.patterns_dir):
            if f.startswith(pattern_id):
                return self._load_json(os.path.join(self.patterns_dir, f))
        return None

    def _generate_candidate_id(self, input_text):
        base_hash = hashlib.sha256(input_text.encode()).hexdigest()[:6]
        if any(x in input_text.lower() for x in ["quota", "limit", "rate", "429"]):
            return f"P-CANDIDATE_RATE_{base_hash}"
        return f"P-CANDIDATE_{base_hash}"

    def crystallize_pattern(self, input_text, analysis):
        candidate_id = self._generate_candidate_id(input_text)
        candidate_filename = f"{candidate_id}.json"
        candidate_path = os.path.join(self.staging_dir, candidate_filename)
        candidate_data = {
            "id": candidate_id,
            "type": "GNOSIS_CANDIDATE",
            "status": "UNREVIEWED",
            "origin_timestamp": analysis.get("timestamp"),
            "surface_narrative": input_text,
            "structural_reality": {
                "detected_markers": self._get_tension_markers(input_text),
                "axiom_violation": analysis.get("axiom_trigger", "UNKNOWN"),
            },
            "generative_synthesis": {"insight": "PENDING ARCHITECT REVIEW", "action": "PENDING"},
        }
        with open(candidate_path, "w", encoding="utf-8") as f:
            json.dump(candidate_data, f, indent=2)
        return candidate_path

    def _handle_rate_limit(self, analysis, input_text):
        analysis.setdefault("resolution", {})
        analysis["resolution"]["kinetic_recovery"] = {
            "option_1": "Add credits (immediate access)",
            "option_2": "Rotate to higher model (if available)",
            "option_3": "Wait for rate limit exhaustion (patience)",
            "recommended": "Wait > Quota > Model Upgrade (per A12 scaling principle)",
        }
        return analysis

    def _process_known_pattern(self, input_text, analysis, pattern_id):
        pattern_data = self._load_pattern(pattern_id)
        if pattern_data:
            pattern_resolution = {
                "pattern_id": pattern_id,
                "name": pattern_data.get("name", ""),
                "resolution_type": pattern_data.get("generative_synthesis", {}).get("type", "block"),
                "insight": pattern_data.get("generative_synthesis", {}).get("insight", "DATA MISSING"),
            }
            analysis.setdefault("pattern_match", []).append(pattern_resolution)
            if "kinetic" in pattern_data.get("generative_synthesis", {}).get("action", "").lower():
                analysis.setdefault("executive_overrides", {})["immediate"] = pattern_data["generative_synthesis"]["action"]
                analysis.setdefault("executive_overrides", {})[
                    "architecture_repair"
                ] = "Permanent solution requires quota increase or process optimization"
        else:
            analysis.setdefault("pattern_match", []).append({
                "pattern_id": pattern_id,
                "name": f"ERROR: Missing pattern file {pattern_id}",
                "resolution_type": "CRITICAL",
                "insight": "Core system health requires this pattern. Recommended: Create crystallization candidate immediately.",
            })

    def gnosis_scan(self, input_text, auto_crystallize=False, rate_limited=False):
        if not self.operator_active:
            print("ERROR: Violation of Axiom A1. Run --init first.")
            return
        print(f"\n>> SCANNING INPUT: '{input_text}'")
        if rate_limited:
            print(">> [SYSTEM ALERT]: RATE_LIMITED=TRUE (FRICTION DETECTED)")
        analysis = {
            "timestamp": str(datetime.now()),
            "input_hash": hashlib.sha256(input_text.encode()).hexdigest()[:8],
            "layer_active": "Layer 1 (Execution)",
            "patterns_detected": [],
            "governance_proposals": [],
        }
        tension_markers = self._get_tension_markers(input_text)
        if tension_markers or rate_limited:
            analysis["status"] = "GNOSIS_BLOCK_DETECTED"
            # P126 - Kinetic Vein
            if rate_limited or ("flow" in input_text.lower() and "limit" in input_text.lower()) or ("rate" in input_text.lower() and "limit" in input_text.lower()):
                p126 = self._load_pattern("P126")
                if p126:
                    analysis["patterns_detected"].append(p126)
                    if rate_limited:
                        analysis["governance_proposals"].append(
                            "PROPOSAL: Add A12 'Flow must scale with friction' to Layer 3."
                        )
                else:
                    analysis.setdefault("errors", []).append("P126 Triggered but file missing.")

            # P119 - Plastiras Inversion
            if "optimize" in input_text.lower() and "pace" in input_text.lower():
                p119 = self._load_pattern("P119")
                if p119:
                    analysis["patterns_detected"].append(p119)
                else:
                    analysis.setdefault("errors", []).append("P119 Triggered but file missing.")

            # Synthesis & Resolution
            if analysis["patterns_detected"]:
                primary = analysis["patterns_detected"][0]
                analysis["resolution"] = {
                    "insight": primary.get("generative_synthesis", {}).get("insight"),
                    "action": primary.get("generative_synthesis", {}).get("action"),
                }
                if rate_limited:
                    self._handle_rate_limit(analysis, input_text)
            else:
                if auto_crystallize:
                    crystal_path = self.crystallize_pattern(input_text, analysis)
                    analysis["resolution"] = f"Novel structural friction. Crystallized at {crystal_path}. Run --review to promote."
                else:
                    analysis["resolution"] = "Novel structural friction detected. Run with --crystallize to capture."
        else:
            # If caller requested automatic crystallization, capture the novel input
            if auto_crystallize:
                crystal_path = self.crystallize_pattern(input_text, analysis)
                analysis["status"] = "GNOSIS_BLOCK_DETECTED"
                analysis["resolution"] = f"Novel structural friction. Crystallized at {crystal_path}. Run --review to promote."
            else:
                analysis["status"] = "NOISE"
                analysis["resolution"] = "Input lacks necessary friction."
        print(json.dumps(analysis, indent=2))
        self.memory.append(analysis)
        return analysis


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MASTER_BRAIN v11.2 [Refactored]")
    parser.add_argument("--init", action="store_true", help="Initialize")
    parser.add_argument("--scan", type=str, help="Input contradiction")
    parser.add_argument("--crystallize", action="store_true", help="Auto-crystallize novel patterns")
    parser.add_argument("--rate-limited", action="store_true", help="Simulate a 429 Rate Limit")

    args = parser.parse_args()
    brain = MasterBrainEngine()
    if args.init:
        brain.initialize()
    if args.scan:
        if not args.init:
            brain.operator_active = True
        brain.gnosis_scan(args.scan, auto_crystallize=args.crystallize, rate_limited=args.rate_limited)
    else:
        parser.print_help()
