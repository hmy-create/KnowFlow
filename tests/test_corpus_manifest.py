from app.corpus.manifest import (
    load_manifest,
)


def test_manifest_contains_14_documents():

    docs = load_manifest()

    assert len(docs) == 14


def test_document_ids_are_unique():

    docs = load_manifest()

    ids = [
        doc.document_id
        for doc in docs
    ]

    assert len(ids) == len(set(ids))


def test_travel_versions():

    docs = {
        doc.document_id: doc
        for doc in load_manifest()
    }

    old = docs[
        "FIN-POL-003__V2.0"
    ]

    new = docs[
        "FIN-POL-003__V2.1"
    ]

    assert str(
        old.effective_at
    ) == "2025-06-01"

    assert str(
        old.expired_at
    ) == "2026-04-30"

    assert str(
        new.effective_at
    ) == "2026-05-01"

    assert new.expired_at is None


def test_conflict_document_same_topic():

    docs = {
        doc.document_id: doc
        for doc in load_manifest()
    }

    assert (
        docs[
            "FIN-POL-003__V2.1"
        ].topic_id
        ==
        docs[
            "FIN-NOTICE-017__V1.0"
        ].topic_id
    )


def test_private_finance_document():

    docs = {
        doc.document_id: doc
        for doc in load_manifest()
    }

    private = docs[
        "FIN-CONF-009__V1.0"
    ]

    assert (
        private.confidentiality
        == "restricted"
    )

    assert (
        private.kb_id
        == "KB_FINANCE_PRIVATE"
    )

    assert set(
        private.allowed_roles
    ) == {
        "finance_manager",
        "admin",
    }


def test_source_files_exist():

    for doc in load_manifest():
        assert doc.source_path.exists()