# Dataset: MS MARCO v1 Passage (TREC DL 2019/2020)

- [msmarco-passage](https://ir-datasets.com/msmarco-passage.html)
- [msmarco-passage/trec-dl-2019/judged](https://ir-datasets.com/msmarco-passage.html#msmarco-passage/trec-dl-2019/judged)
- [msmarco-passage/trec-dl-2020/judged](https://ir-datasets.com/msmarco-passage.html#msmarco-passage/trec-dl-2020/judged)
- [Notebook](msmarco-v1-passage.ipynb)

## Obtain the corpus

Unlike Robust/NTCIR, MS MARCO requires no license agreement. `ir_datasets`
downloads the corpus (~2.9 GB, 8,841,823 passages) automatically on first
access and caches it under `~/.ir_datasets/msmarco-passage/`.

```python
import ir_datasets
dataset = ir_datasets.load("msmarco-passage")
docstore = dataset.docs_store()
docstore.build()
```

Direct download URLs (fallback / reference only):

- Corpus: <https://msmarco.z22.web.core.windows.net/msmarcoranking/collection.tar.gz>
- Qrels 2019: <https://trec.nist.gov/data/deep/2019qrels-pass.txt>
- Qrels 2020: <https://trec.nist.gov/data/deep/2020qrels-pass.txt>

Document fields and sample data

```python
print(dataset.docs_cls().__annotations__)
# {'doc_id': <class 'str'>, 'text': <class 'str'>}
```

Note: passages have a single `text` field (no title).

## Obtain the queries/qrels

Use the `judged` variants so only queries with NIST judgments are included.

```python
dl2019 = ir_datasets.load("msmarco-passage/trec-dl-2019/judged")  # 43 queries,  9,260 qrels
dl2020 = ir_datasets.load("msmarco-passage/trec-dl-2020/judged")  # 54 queries, 11,386 qrels
```

Query fields and data

```python
print(dl2019.queries_cls().__annotations__)
# {'query_id': <class 'str'>, 'text': <class 'str'>}
```

Qrels are graded (0-3): 0 irrelevant, 1 related, 2 highly relevant, 3 perfectly relevant.
For binary metrics (e.g. MAP), the track convention is relevance >= 2.

```python
print(dl2019.qrels_cls().__annotations__)
# {'query_id': <class 'str'>, 'doc_id': <class 'str'>, 'relevance': <class 'int'>, 'iteration': <class 'str'>}
```

## Notes

- TREC DL 2019/2020 also ran a **document ranking** task on the separate
  MS MARCO v1 document corpus (3.2M documents, ~22 GB, different doc IDs and
  qrels). To be added later as `msmarco-v1-document` if needed.
