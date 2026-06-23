# Dataset: SciDocs

- [beir/scidocs](https://ir-datasets.com/beir.html#beir/scidocs)
- [Notebook](scidocs.ipynb)

## Obtain a dataset


```python
import ir_datasets
dataset_name = "beir/scidocs"
dataset = ir_datasets.load(dataset_name)
docstore = dataset.docs_store()
docstore.build()
```

Document fields and sample data

```python
print(dataset.docs_cls().__annotations__)
# {'doc_id': <class 'str'>, 'text': <class 'str'>, 'title': <class 'str'>, 'authors': typing.List[str], 'year': <class 'int'>, 'cited_by': typing.List[str], 'references': typing.List[str]}
```

```python
doc_id='632589828c8b9fca2c3a59e97451fde8fa7d188d'
print(docstore.get(doc_id).title)
print(docstore.get(doc_id).text)
# A hybrid of genetic algorithm and ...
# An evolutionary recurrent network ...
```

Query fields and data

```python
print(dataset.queries_cls().__annotations__)
# {'query_id': <class 'str'>, 'text': <class 'str'>, 'authors': typing.List[str], 'year': <class 'int'>, 'cited_by': typing.List[str], 'references': typing.List[str]}
```

```python
import pandas as pd
pd.DataFrame(dataset.queries_iter())
# query_id	text	authors	year	cited_by	references
# 0	78495383450e02c5fe817e408726134b3084905d	A Direct Search Method to solve ...	[50306438, 15303316, 1976596]	2014.0	[38e78343cfd5c013decf49e8cf008ddf6458200f]	[632589828c8b9fca2c3a59e97451fde8fa7d188d, 4cf...
# ...
# 1000 rows × 6 columns
```

Qrel fields and data

```python
print(dataset.qrels_cls().__annotations__)
# {'query_id': <class 'str'>, 'doc_id': <class 'str'>, 'relevance': <class 'int'>, 'iteration': <class 'str'>}
```

```python
pd.DataFrame(dataset.qrels_iter())
# query_id	doc_id	relevance	iteration
# 0	78495383450e02c5fe817e408726134b3084905d	632589828c8b9fca2c3a59e97451fde8fa7d188d	1	0
# ...
# 29928 rows × 4 columns
```