import os

import pytest

from app.core.response_assembler import (
    assemble_citations,
)


RUN_LIVE = (
    os.getenv(
        "RUN_LIVE_CITATION_TESTS"
    )
    == "1"
)


@pytest.mark.skipif(
    not RUN_LIVE,
    reason="Live citation test disabled",
)
def test_product_refund_citation():

    trace_id = "TR-TEST-CITATION"

    citations = assemble_citations(
        trace_id=trace_id,
        evidence_ids=[
            "PROD-POL-A-004__V2.0__C001"
        ],
    )

    assert len(citations) == 1

    item = citations[0]

    assert (
        item.chunk_id
        == "PROD-POL-A-004__V2.0__C001"
    )

    assert (
        item.document_id
        == "PROD-POL-A-004__V2.0"
    )

    assert (
        item.version_no
        == "V2.0"
    )

    assert item.section

    assert (
        "14个自然日"
        in item.original_text
    )