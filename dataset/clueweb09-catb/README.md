# Dataset: ClueWeb09 Category B (TREC Web Track 2009-2012, diversity task)

- [clueweb09/catb](https://ir-datasets.com/clueweb09.html#clueweb09/catb)
- [clueweb09/catb/trec-web-2009/diversity](https://ir-datasets.com/clueweb09.html#clueweb09/catb/trec-web-2009/diversity) (and 2010/2011/2012)
- [Notebook](clueweb09-catb.ipynb)

50,220,423 English web pages (WARC/HTML), the "Category B" subset of the
ClueWeb09 crawl. Pages were truncated at crawl time (~256 KB), so document
size is naturally bounded.

## Obtain the corpus

ClueWeb09 is a licensed corpus: obtain it from CMU (see Data Access
Information on the [ir_datasets page](https://ir-datasets.com/clueweb09.html))
and place it under `~/.ir_datasets/clueweb09/corpus`. Queries and qrels
download automatically.

Documents are raw `WarcDoc`s (bytes HTML). Use `doc.default_text()` for
HTML-to-text extraction; the extracted title arrives on the first line
(some pages produce a single line with no newline -- treat those as body
only).

```python
import ir_datasets
dataset = ir_datasets.load("clueweb09/catb")
doc = next(dataset.docs_iter())
print(doc.default_text()[:200])
```

## Obtain the queries/qrels

The **diversity task** variants of the TREC Web Track 2009-2012 (50 topics
per year). Each topic carries subtopics (faceted/ambiguous), and qrels are
judged per subtopic.

```python
dl = ir_datasets.load("clueweb09/catb/trec-web-2009/diversity")
```

Relevance grades include **-2 (spam)**. Standard practice in the ClueWeb09
literature additionally filters the spammiest ~30% of the corpus using the
Waterloo Fusion spam scores (threshold 70) -- not applied in our indexing
notebook, but worth remembering when comparing against published numbers.

## Evaluation

Evaluation is handled with the [ir_measures](https://ir-measur.es/) library,
whose `ndeval` provider supplies the diversity measures used by the track:

```python
import ir_measures
from ir_measures import parse_measure
measures = [parse_measure("alpha_nDCG@10"), parse_measure("ERR_IA@10"), parse_measure("NRBP")]
ir_measures.calc_aggregate(measures, dataset.qrels_iter(), run)
```
