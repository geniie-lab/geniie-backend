# Dataset: TREC Robust 2005

- [aquaint/trec-robust-2005](https://ir-datasets.com/aquaint.html#aquaint/trec-robust-2005)
- [Notebook](trec-robust-2005.ipynb)

## Obtain the corpus

See Data Access Information of [AQUAINT - ir_datasets](https://ir-datasets.com/aquaint.html) to learn how to obtain the AQUAINT corpus and where to save the file.

## Obtain the queries/qrels


```python
import ir_datasets
dataset_name = "aquaint/trec-robust-2005"
dataset = ir_datasets.load(dataset_name)
docstore = dataset.docs_store()
docstore.build()
```

Document fields and sample data

```python
print(dataset.docs_cls().__annotations__)
# {'doc_id': <class 'str'>, 'text': <class 'str'>, 'marked_up_doc': <class 'str'>}
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
# 37798 rows × 4 columns
```