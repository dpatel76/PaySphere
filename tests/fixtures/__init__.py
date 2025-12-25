"""Test fixtures for GPS CDM ingestion framework."""

from pathlib import Path

FIXTURES_DIR = Path(__file__).parent

# Sample message paths
PAIN001_SAMPLE = FIXTURES_DIR / "pain001_sample.xml"
MT103_SAMPLE = FIXTURES_DIR / "mt103_sample.txt"


def load_pain001_sample() -> str:
    """Load sample pain.001 XML message."""
    return PAIN001_SAMPLE.read_text()


def load_mt103_sample() -> str:
    """Load sample MT103 message."""
    return MT103_SAMPLE.read_text()
