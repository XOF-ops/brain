import os
import sys
import json
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.master_brain import MasterBrainEngine


def setup_engine(tmpdir):
    patterns_dir = os.path.join(tmpdir, 'patterns')
    staging_dir = os.path.join(tmpdir, 'staging')
    os.makedirs(patterns_dir, exist_ok=True)
    os.makedirs(staging_dir, exist_ok=True)
    # Copy our pattern files into tmp patterns for isolation
    here = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    orig_patterns = os.path.join(here, 'patterns')
    for f in os.listdir(orig_patterns):
        shutil.copy(os.path.join(orig_patterns, f), patterns_dir)
    engine = MasterBrainEngine(patterns_dir=patterns_dir, staging_dir=staging_dir)
    engine.operator_active = True
    return engine


def test_rate_limited_detection_and_kinetic_recovery(tmp_path):
    engine = setup_engine(str(tmp_path))
    analysis = engine.gnosis_scan("We are being rate limited by quota and 429 errors", rate_limited=True)
    assert analysis['status'] == 'GNOSIS_BLOCK_DETECTED'
    # Should have P126 in patterns_detected (the loaded pattern objects)
    assert any(p.get('id') == 'P126' or p.get('name') == 'The Kinetic Vein' for p in analysis['patterns_detected'])
    # Should include kinetic_recovery in resolution
    assert 'kinetic_recovery' in analysis['resolution']
    # Governance proposals should include A12 proposal
    assert any('A12' in p for p in analysis['governance_proposals'])


def test_multi_pattern_detection(tmp_path):
    engine = setup_engine(str(tmp_path))
    # Input triggers both P119 and P126 via keywords
    analysis = engine.gnosis_scan("We must optimize pace but the rate limit blocks us", rate_limited=True)
    assert analysis['status'] == 'GNOSIS_BLOCK_DETECTED'
    assert len(analysis['patterns_detected']) >= 1
    # Ensure primary resolution exists
    assert 'insight' in analysis['resolution']


def test_crystallize_candidate(tmp_path):
    engine = setup_engine(str(tmp_path))
    # Use an input that doesn't match triggers to force crystallization
    analysis = engine.gnosis_scan("A novel kind of friction: ephemeral silence.", auto_crystallize=True)
    assert 'Crystallized at' in analysis['resolution']
    # Ensure a candidate file was created
    files = os.listdir(engine.staging_dir)
    assert any(f.startswith('P-CANDIDATE') for f in files)
