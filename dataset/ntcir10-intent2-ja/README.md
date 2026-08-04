# NTCIR-10 INTENT-2 Japanese Document Ranking (`ntcir10-intent2-ja`)

Registers the Japanese Document Ranking data of the NTCIR-10 INTENT-2 task
with ir_datasets: 100 topics (0301–0400) with fac/amb/nav topic tags,
intents (subtopics with probabilities and nav/inf intent types), and
per-intent graded relevance judgments (L0–L4) over ClueWeb09-JA documents.

## Obtaining the data

The INTENT-2 research-purpose data is distributed by NII/IDR under a research
agreement: https://www.nii.ac.jp/dsc/idr/en/ntcir/ntcir-taskdata.html
(NTCIR-10 INTENT-2 task). The ClueWeb09-JA document corpus is licensed
separately from CMU: https://lemurproject.org/clueweb09/

## Setup

Place these files from the INTENT-2 distribution into
`~/.ir_datasets/ntcir10-intent2-ja/`:

- `ntcir10intent.0301-0400.full-revised.xml`
- `INTENT-2DRJ.Dqrels`
- `INTENT-2DRJ.5-4.DINprob` (optional; supplies nav/inf intent types when the
  XML lacks them)

## Usage

```python
import ntcir10_intent2_ja  # registers the dataset on import
import ir_datasets
ds = ir_datasets.load('ntcir10-intent2-ja')
for q in ds.queries_iter():
    ...  # q.query_id, q.query, q.type (fac/amb/nav), q.subtopics
         # (number, probability, intent_type, description)
for qrel in ds.qrels_iter():
    ...  # query_id, doc_id, relevance (0-4), iteration = intent number
```

The distribution's Chinese (0201–0299) and English (0401–0450, Subtopic
Mining only — no Document Ranking) topics are out of scope here.
