# NTCIR-9 INTENT-1 Japanese Document Ranking (`ntcir9-intent1-ja`)

Registers the Japanese Document Ranking data of the NTCIR-9 INTENT-1 task
with ir_datasets: 100 topics (0101–0200) with intents (subtopics carrying
probabilities) and per-intent graded relevance judgments (L0–L4) over
ClueWeb09-JA documents.

## Obtaining the data

The INTENT-1 research-purpose data is distributed by NII/IDR under a research
agreement: https://www.nii.ac.jp/dsc/idr/en/ntcir/ntcir-taskdata.html
(NTCIR-9 INTENT task). The ClueWeb09-JA document corpus is licensed
separately from CMU: https://lemurproject.org/clueweb09/

## Setup

Place these files from the INTENT-1 distribution into
`~/.ir_datasets/ntcir9-intent1-ja/`:

- `ntcir9intent.0101-0200.full.xml`
- `ntcir9intent.0101-0200.dr.Dqrels`

## Usage

```python
import ntcir9_intent1_ja  # registers the dataset on import
import ir_datasets
ds = ir_datasets.load('ntcir9-intent1-ja')
for q in ds.queries_iter():
    ...  # q.query_id, q.query, q.subtopics (number, probability, description)
for qrel in ds.qrels_iter():
    ...  # query_id, doc_id, relevance (0-4), iteration = intent number
```

Topics 0001–0100 in the same distribution are Chinese; they are out of scope
here.
