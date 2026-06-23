# Dataset: TREC Robust 2004

- [disks45/nocr/trec-robust-2004](https://ir-datasets.com/disks45.html#disks45/nocr/trec-robust-2004)
- [Notebook](trec-robust-2004.ipynb)

## Obtain the corpus

See Data Access Information of [TREC Disks 4 and 5 - ir_datasets](https://ir-datasets.com/disks45.html) to learn how to obtain the  corpus and where to save the file. Here we use `nocr` version.

## Obtain the queries/qrels


```python
import ir_datasets
dataset_name = "disks45/nocr/trec-robust-2004"
dataset = ir_datasets.load(dataset_name)
docstore = dataset.docs_store()
docstore.build()
```

Document fields and sample data

```python
print(dataset.docs_cls().__annotations__)
# {'doc_id': <class 'str'>, 'title': <class 'str'>, 'body': <class 'str'>, 'marked_up_doc': <class 'bytes'>}
```

```python
doc_id='APW19980609.1531'
print(docstore.get(doc_id).text)
```

Query fields and data

```python
print(dataset.queries_cls().__annotations__)
# {'query_id': <class 'str'>, 'title': <class 'str'>, 'description': <class 'str'>, 'narrative': <class 'str'>}
```

```python
import pandas as pd
pd.DataFrame(dataset.queries_iter())
# 	query_id	title	description	narrative
# ...
# 250 rows × 4 columns
```

Qrel fields and data

```python
print(dataset.qrels_cls().__annotations__)
# {'query_id': <class 'str'>, 'doc_id': <class 'str'>, 'relevance': <class 'int'>, 'iteration': <class 'str'>}
```

```python
pd.DataFrame(dataset.qrels_iter())
# query_id	doc_id	relevance	iteration
# ...
# 311410 rows × 4 columns
```