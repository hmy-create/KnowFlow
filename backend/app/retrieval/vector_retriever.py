from functools import lru_cache

import numpy as np
import torch
from FlagEmbedding import BGEM3FlagModel

from app.models import (
    Chunk,
    RetrievalCandidate,
)


@lru_cache(maxsize=1)
def get_embedding_model():
    return BGEM3FlagModel(
        "BAAI/bge-m3",
        use_fp16=torch.cuda.is_available(),
    )


def encode_dense(
    texts: list[str],
) -> np.ndarray:

    model = get_embedding_model()

    output = model.encode(
        texts,
        return_dense=True,
        return_sparse=False,
        return_colbert_vecs=False,
    )

    return np.asarray(
        output["dense_vecs"],
        dtype=np.float32,
    )


def vector_retrieve(
    query: str,
    chunks: list[Chunk],
    top_n: int = 20,
) -> list[RetrievalCandidate]:

    if not chunks:
        return []

    query_vector = encode_dense(
        [query]
    )[0]

    document_vectors = encode_dense(
        [
            chunk.text
            for chunk in chunks
        ]
    )

    # BGE-M3 dense embedding 已归一化，
    # dot product 可作为相似度。
    scores = (
        document_vectors
        @ query_vector
    )

    ranked_indices = np.argsort(
        scores
    )[::-1]

    results = []

    for index in ranked_indices[
        :top_n
    ]:
        chunk = chunks[int(index)]

        score = float(
            scores[int(index)]
        )

        results.append(
            RetrievalCandidate(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                text=chunk.text,
                page=chunk.page,
                section=chunk.section,
                chunk_index=chunk.chunk_index,
                retrieval_source="vector",
                raw_score={
                    "vector": score
                },
            )
        )

    return results