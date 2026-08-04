# TREC Web Track Diversity qrels 2009-2012 (`trec-web-<year>-diversity`)

Registers the official per-subtopic diversity judgments of the TREC Web
Track 2009-2012 with ir_datasets, as `trec-web-2009-diversity` through
`trec-web-2012-diversity`. Topics (with subtopics) are reused from the
built-in `clueweb09/en/trec-web-<year>` datasets; only the qrels differ —
the built-ins expose the ad-hoc judgments, these expose the diversity ones
with the subtopic number in the iteration field.

## Obtaining the data

Freely downloadable from trec.nist.gov (no agreement needed):

- 2009: https://trec.nist.gov/data/web/09/qrels.diversity.gz
- 2010: https://trec.nist.gov/data/web/10/10.diversity-qrels.final
- 2011: https://trec.nist.gov/data/web/11/qrels.diversity
- 2012: https://trec.nist.gov/data/web/12/qrels.diversity

The ClueWeb09 document corpus is licensed separately from CMU:
https://lemurproject.org/clueweb09/

## Setup

Place the four files into `~/.ir_datasets/trec-web-diversity/`, prefixed
with the year so the names don't collide:

- `2009.qrels.diversity.gz`
- `2010.10.diversity-qrels.final`
- `2011.qrels.diversity`
- `2012.qrels.diversity`

## Usage

```python
import trec_web_diversity  # registers the datasets on import
import ir_datasets
ds = ir_datasets.load('trec-web-2012-diversity')
for q in ds.queries_iter():
    ...  # query_id, query, description, type, subtopics
for qrel in ds.qrels_iter():
    ...  # query_id, doc_id, relevance, iteration = subtopic number
```

Format notes: the 2010 file lists relevant pairs only (absent pairs count
as nonrelevant, per ndeval convention); 2011/2012 use -2 for spam; 2011
onward judgments are graded.
