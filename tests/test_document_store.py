"""Tests for the Document Store (SQLite backend)."""

import pytest

from neural_lattice.document_store import DocumentStore
from neural_lattice.metadata_engine import MetadataEngine


@pytest.fixture
def store():
    return DocumentStore(":memory:")


@pytest.fixture
def sample_meta():
    return MetadataEngine.generate(
        doc_id="TST-DOC-001",
        title="Test Document",
        cognitive_load=8,
        tags=["test", "sample"],
    )


class TestCreate:
    def test_creates_document(self, store, sample_meta):
        doc = store.create(sample_meta, content="Hello world")
        assert doc["doc_id"] == "TST-DOC-001"
        assert doc["content"] == "Hello world"
        assert doc["zone"] == "GREEN"

    def test_rejects_invalid_metadata(self, store):
        with pytest.raises(ValueError, match="Invalid metadata"):
            store.create({"doc_id": "bad"})

    def test_duplicate_raises(self, store, sample_meta):
        store.create(sample_meta)
        with pytest.raises(Exception):
            store.create(sample_meta)


class TestGet:
    def test_retrieves_document(self, store, sample_meta):
        store.create(sample_meta)
        doc = store.get("TST-DOC-001")
        assert doc is not None
        assert doc["title"] == "Test Document"

    def test_returns_none_for_missing(self, store):
        assert store.get("NOPE-DOC-999") is None


class TestUpdate:
    def test_updates_fields(self, store, sample_meta):
        store.create(sample_meta)
        doc = store.update("TST-DOC-001", {"title": "Updated Title"})
        assert doc["title"] == "Updated Title"

    def test_update_missing_raises(self, store):
        with pytest.raises(KeyError):
            store.update("NOPE-DOC-999", {"title": "Nope"})

    def test_updates_tags(self, store, sample_meta):
        store.create(sample_meta)
        doc = store.update("TST-DOC-001", {"tags": ["new_tag"]})
        assert doc["tags"] == ["new_tag"]


class TestDelete:
    def test_deletes_document(self, store, sample_meta):
        store.create(sample_meta)
        assert store.delete("TST-DOC-001") is True
        assert store.get("TST-DOC-001") is None

    def test_delete_missing_returns_false(self, store):
        assert store.delete("NOPE-DOC-999") is False


class TestSearch:
    def test_search_by_zone(self, store, sample_meta):
        store.create(sample_meta)
        results = store.search(zone="GREEN")
        assert len(results) == 1

    def test_search_by_tag(self, store, sample_meta):
        store.create(sample_meta)
        results = store.search(tag="test")
        assert len(results) == 1

    def test_search_by_text(self, store, sample_meta):
        store.create(sample_meta, content="unique content here")
        results = store.search(q="unique")
        assert len(results) == 1

    def test_search_empty(self, store):
        results = store.search(zone="RED")
        assert results == []


class TestCountByZone:
    def test_counts(self, store, sample_meta):
        store.create(sample_meta)
        meta2 = MetadataEngine.generate("TST-DOC-002", "Another", cognitive_load=2)
        store.create(meta2)
        counts = store.count_by_zone()
        assert counts["GREEN"] == 1
        assert counts["RED"] == 1
        assert counts["YELLOW"] == 0


class TestListAll:
    def test_lists_all_documents(self, store, sample_meta):
        store.create(sample_meta)
        meta2 = MetadataEngine.generate("TST-DOC-002", "Second", cognitive_load=5)
        store.create(meta2)
        docs = store.list_all()
        assert len(docs) == 2
