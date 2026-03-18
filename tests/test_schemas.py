"""Tests for metadata schema validation (Charter Section 3.3)."""

import pytest

from neural_lattice.meta.schemas import (
    validate_doc_id,
    validate_tag,
    validate_metadata,
    validate_cognitive_load_for_zone,
    ZoneEnum,
)


class TestDocIdValidation:
    def test_valid_ids(self):
        assert validate_doc_id("NLCA-CHAR-001")
        assert validate_doc_id("TST-DOC-999")
        assert validate_doc_id("SDLC-CHART-100")

    def test_invalid_ids(self):
        assert not validate_doc_id("bad-id")
        assert not validate_doc_id("lowercase-id-001")
        assert not validate_doc_id("AB-CD-001")  # too short
        assert not validate_doc_id("ABCDE-ABCDEFG-001")  # too long


class TestTagValidation:
    def test_valid_tags(self):
        assert validate_tag("design")
        assert validate_tag("api_docs")
        assert validate_tag("sprint1")

    def test_invalid_tags(self):
        assert not validate_tag("Design")  # uppercase
        assert not validate_tag("has-dash")
        assert not validate_tag("1starts_number")
        assert not validate_tag("")


class TestCognitiveLoadZoneAlignment:
    def test_green_range(self):
        assert validate_cognitive_load_for_zone(ZoneEnum.GREEN, 7)
        assert validate_cognitive_load_for_zone(ZoneEnum.GREEN, 10)
        assert not validate_cognitive_load_for_zone(ZoneEnum.GREEN, 6)

    def test_yellow_range(self):
        assert validate_cognitive_load_for_zone(ZoneEnum.YELLOW, 4)
        assert validate_cognitive_load_for_zone(ZoneEnum.YELLOW, 6)
        assert not validate_cognitive_load_for_zone(ZoneEnum.YELLOW, 7)

    def test_red_range(self):
        assert validate_cognitive_load_for_zone(ZoneEnum.RED, 1)
        assert validate_cognitive_load_for_zone(ZoneEnum.RED, 3)
        assert not validate_cognitive_load_for_zone(ZoneEnum.RED, 4)


class TestValidateMetadata:
    def test_fully_valid(self):
        meta = {
            "doc_id": "TST-DOC-001",
            "title": "Test Document",
            "zone": "GREEN",
            "protocol": "Onset_Omega_1",
            "artifact_type": "note",
            "cognitive_load": 8,
            "timestamp": "2026-03-17T00:00:00+00:00",
            "dependencies": [],
            "tags": ["test"],
            "status": "DRAFT",
        }
        assert validate_metadata(meta) == []

    def test_missing_fields(self):
        errors = validate_metadata({})
        assert len(errors) == 10  # all 10 required

    def test_invalid_cognitive_load_type(self):
        meta = {
            "doc_id": "TST-DOC-001",
            "title": "Test",
            "zone": "GREEN",
            "protocol": "Onset_Omega_1",
            "artifact_type": "note",
            "cognitive_load": "high",
            "timestamp": "2026-03-17T00:00:00+00:00",
            "dependencies": [],
            "tags": [],
            "status": "DRAFT",
        }
        errors = validate_metadata(meta)
        assert any("cognitive_load" in e for e in errors)
