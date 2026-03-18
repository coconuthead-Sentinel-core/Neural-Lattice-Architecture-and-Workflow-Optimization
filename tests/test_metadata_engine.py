"""Tests for the Metadata Engine (Charter Section 3.3)."""

import pytest
import yaml

from neural_lattice.metadata_engine import MetadataEngine
from neural_lattice.meta.schemas import ArtifactType, ProtocolEnum, ZoneEnum


class TestGenerate:
    def test_generates_all_10_fields(self):
        meta = MetadataEngine.generate(
            doc_id="NLCA-CHAR-001",
            title="Test Document",
            cognitive_load=8,
        )
        required = [
            "doc_id", "title", "zone", "protocol", "artifact_type",
            "cognitive_load", "timestamp", "dependencies", "tags", "status",
        ]
        for field in required:
            assert field in meta, f"Missing field: {field}"

    def test_auto_classifies_green(self):
        meta = MetadataEngine.generate("TST-DOC-001", "Test", cognitive_load=8)
        assert meta["zone"] == "GREEN"

    def test_auto_classifies_yellow(self):
        meta = MetadataEngine.generate("TST-DOC-002", "Test", cognitive_load=5)
        assert meta["zone"] == "YELLOW"

    def test_auto_classifies_red(self):
        meta = MetadataEngine.generate("TST-DOC-003", "Test", cognitive_load=2)
        assert meta["zone"] == "RED"

    def test_explicit_zone_override(self):
        meta = MetadataEngine.generate(
            "TST-DOC-004", "Test", cognitive_load=8, zone="GREEN"
        )
        assert meta["zone"] == "GREEN"

    def test_custom_tags_and_deps(self):
        meta = MetadataEngine.generate(
            "TST-DOC-005", "Test", cognitive_load=5,
            tags=["design", "api"], dependencies=["TST-DOC-001"],
        )
        assert meta["tags"] == ["design", "api"]
        assert meta["dependencies"] == ["TST-DOC-001"]


class TestValidate:
    def test_valid_metadata(self):
        meta = MetadataEngine.generate("TST-DOC-001", "Valid Doc", cognitive_load=8)
        errors = MetadataEngine.validate(meta)
        assert errors == []

    def test_invalid_doc_id(self):
        meta = MetadataEngine.generate("TST-DOC-001", "Test", cognitive_load=8)
        meta["doc_id"] = "bad-id"
        errors = MetadataEngine.validate(meta)
        assert any("doc_id" in e for e in errors)

    def test_missing_field(self):
        meta = MetadataEngine.generate("TST-DOC-001", "Test", cognitive_load=8)
        del meta["title"]
        errors = MetadataEngine.validate(meta)
        assert any("title" in e for e in errors)

    def test_load_zone_mismatch(self):
        meta = MetadataEngine.generate("TST-DOC-001", "Test", cognitive_load=8)
        meta["zone"] = "RED"  # mismatch: load 8 is GREEN
        errors = MetadataEngine.validate(meta)
        assert any("cognitive_load" in e for e in errors)


class TestYamlSerialization:
    def test_roundtrip(self):
        meta = MetadataEngine.generate("TST-DOC-001", "Test", cognitive_load=5)
        yaml_str = MetadataEngine.to_yaml(meta)
        parsed = MetadataEngine.from_yaml(yaml_str)
        assert parsed["doc_id"] == "TST-DOC-001"
        assert parsed["zone"] == "YELLOW"

    def test_frontmatter_format(self):
        meta = MetadataEngine.generate("TST-DOC-001", "Test", cognitive_load=5)
        fm = MetadataEngine.to_frontmatter(meta)
        assert fm.startswith("---\n")
        assert fm.endswith("---\n")

    def test_extract_frontmatter(self):
        meta = MetadataEngine.generate("TST-DOC-001", "Test", cognitive_load=5)
        fm = MetadataEngine.to_frontmatter(meta)
        content = fm + "Body text here."
        extracted, body = MetadataEngine.extract_frontmatter(content)
        assert extracted is not None
        assert extracted["doc_id"] == "TST-DOC-001"
        assert body == "Body text here."

    def test_no_frontmatter(self):
        extracted, body = MetadataEngine.extract_frontmatter("No frontmatter here")
        assert extracted is None
        assert body == "No frontmatter here"
