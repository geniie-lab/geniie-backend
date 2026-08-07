# Retrieval by OpenSearch

One notebook per ranker × index structure (minimum variance per notebook);
every notebook ends with the same optional reranking section
(`rerank_bge_m3` search pipeline, `BAAI/bge-reranker-v2-m3`).

## Title+text / nested-chunk indexes (TREC Robust, NTCIR, SciDocs, MS MARCO v1 document)

- [BM25](opensearch_bm25_search.ipynb)
- [SPLADE (Sparse Encoder)](opensearch_splade_search.ipynb)
- [DPR (Dense Encoder)](opensearch_dpr_search.ipynb)

## Flat title-less indexes (MS MARCO v1 passage)

- [BM25](opensearch_bm25_search_msmarco_passage.ipynb)
- [SPLADE (Sparse Encoder)](opensearch_splade_search_msmarco_passage.ipynb)
- [DPR (Dense Encoder)](opensearch_dpr_search_msmarco_passage.ipynb)

Query-model IDs come from
[ml_model_registration.ipynb](../indexing/opensearch/ml_model_registration.ipynb)
(`*_query_model_id` variables); the reranker pipeline is created there too.
