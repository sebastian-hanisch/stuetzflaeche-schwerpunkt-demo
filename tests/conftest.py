"""Gemeinsame Fixtures: die Mini-Instanz, an der jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stz_scenario import Instance  # noqa: E402


@pytest.fixture
def mini():
    """Vier Quader (Breite, Tiefe, Höhe) = (2, 8, 2), (4, 7, 4), (3, 8, 6), (4, 8, 3) mit den Nummern 0 bis 3 und den Massen 1, 3, 3, 1; Behälter 10 mal 10 mal 10, Volumen 384, Schranke 1.

    Von Hand gerechnet (Details in tests/test_algorithm.py): Ohne Stützbedingung liegt Quader 3 bei (0, 0, 4) auf 43,75 % Stützfläche, mit 80 % bei (2, 0, 4) auf 87,5 %, mit 100 % braucht er einen
    neuen Behälter."""
    return Instance(((2, 8, 2), (4, 7, 4), (3, 8, 6), (4, 8, 3)), (1.0, 3.0, 3.0, 1.0), 10)
