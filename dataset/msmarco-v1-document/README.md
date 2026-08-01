# Dataset: MS MARCO v1 Document (TREC DL 2019/2020)

- [msmarco-document](https://ir-datasets.com/msmarco-document.html)
- [msmarco-document/trec-dl-2019/judged](https://ir-datasets.com/msmarco-document.html#msmarco-document/trec-dl-2019/judged)
- [msmarco-document/trec-dl-2020/judged](https://ir-datasets.com/msmarco-document.html#msmarco-document/trec-dl-2020/judged)
- [Notebook](msmarco-v1-document.ipynb)

The corpus for the TREC DL 2019/2020 **document ranking** task. Built by
mapping the [MS MARCO v1 passages](../msmarco-v1-passage/README.md) back to
their source pages, but doc IDs (`D...`) and qrels are **independent** of the
passage ones — the two tasks cannot be mixed.

## Obtain the corpus

No license agreement required. `ir_datasets` downloads the corpus (~22 GB,
3,213,835 documents) automatically on first access and caches it under
`~/.ir_datasets/msmarco-document/`. Download + docstore build take
considerably longer than the passage corpus.

```python
import ir_datasets
dataset = ir_datasets.load("msmarco-document")
docstore = dataset.docs_store()
docstore.build()
```

Document fields and sample data

```python
print(dataset.docs_cls().__annotations__)
# {'doc_id': <class 'str'>, 'url': <class 'str'>, 'title': <class 'str'>, 'body': <class 'str'>}
```

Documents are full web pages (~1,100 words on average, with a long tail);
downstream encoder indexing truncates `body` (see the indexing notebooks),
while BM25 indexes it in full.

## Obtain the queries/qrels

Use the `judged` variants so only queries with NIST judgments are included.

```python
dl2019 = ir_datasets.load("msmarco-document/trec-dl-2019/judged")  # 43 queries
dl2020 = ir_datasets.load("msmarco-document/trec-dl-2020/judged")  # 45 queries
```

Qrels are graded (0-3). Note the document-task judging used slightly
different grade semantics than the passage task (see the track overview
papers); the track convention for binary metrics is relevance >= 1 for
documents (vs >= 2 for passages).
