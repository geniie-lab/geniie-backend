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

### Topics and qrels

Place these files from the INTENT-2 distribution into
`~/.ir_datasets/ntcir10-intent2-ja/`:

- `ntcir10intent.0301-0400.full-revised.xml`
- `INTENT-2DRJ.Dqrels`
- `INTENT-2DRJ.5-4.DINprob` (optional; supplies nav/inf intent types when the
  XML lacks them)

### Documents

Documents are proxied from ir_datasets' built-in `clueweb09/ja`, so they must
sit where that dataset expects them:

```
~/.ir_datasets/clueweb09/corpus/ClueWeb09_Japanese_1/            (ja0000-ja0012)
~/.ir_datasets/clueweb09/corpus/ClueWeb09_Japanese_2/            (ja0013-ja0016)
~/.ir_datasets/clueweb09/corpus/record_counts/ClueWeb09_Japanese_{1,2}_counts.txt
```

CMU's `download-cw09-ntcir-intent.sh` writes all of these one level deeper,
under `corpus/ClueWeb09-NTCIR-Intent/` — move them up as above, or
`clueweb09/ja` fails with a `FileNotFoundError` naming the path it wanted.
Record-position checkpoints for the Japanese WARCs ship with ir_datasets
(`corpus.chk/ClueWeb09_Japanese_{1,2}/`), so `docs_store()` lookups seek
directly and need no build step.

Verified totals: 1,605 WARC files, 67,337,717 documents, ~221 GB.

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

doc = ds.docs_store().get('clueweb09-ja0002-53-16670')
doc.default_text()   # decoded text; first line is the HTML title
```

### Working with the documents

`docs_cls()` is ClueWeb09's WARC document: `doc_id`, `url`, `date`,
`http_headers`, `body`, `body_content_type`.

- `body` is **raw HTML bytes**, not str — running a str regex over it raises
  `cannot use a string pattern on a bytes-like object`.
- Use `default_text()`, which strips tags and returns str. Pages are commonly
  Shift_JIS (2009-era Japanese web) and often declare the charset only in a
  `<meta>` tag; `default_text()` decodes them correctly.
- There is no `title` field: the **first line** of `default_text()` is the
  HTML title, the rest is body text.

## Evaluation

Qrels carry the intent number in `iteration`, which is the shape
[ir_measures](https://ir-measur.es/)' `ndeval`/`pyndeval` provider expects, so
diversity measures work directly:

```python
import ir_measures
from ir_measures import parse_measure
measures = [parse_measure('alpha_nDCG@20'), parse_measure('ERR_IA@20'), parse_measure('NRBP')]
ir_measures.calc_aggregate(measures, ds.qrels_iter(), run)
```

Gotchas: pyndeval caps cutoffs at 20 (no `@100`); `calc_aggregate` averages
over every topic in the qrels, so restrict them to your topic subset first;
and five topics (**0356, 0363, 0367, 0370, 0371**) have no Document Ranking
qrels at all — exclude them rather than treating the absence as a parsing bug.

The distribution's Chinese (0201–0299) and English (0401–0450, Subtopic
Mining only — no Document Ranking) topics are out of scope here.
