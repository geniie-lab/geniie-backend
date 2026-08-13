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

### Topics and qrels

Place these files from the INTENT-1 distribution into
`~/.ir_datasets/ntcir9-intent1-ja/`:

- `ntcir9intent.0101-0200.full.xml`
- `ntcir9intent.0101-0200.dr.Dqrels`

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
import ntcir9_intent1_ja  # registers the dataset on import
import ir_datasets
ds = ir_datasets.load('ntcir9-intent1-ja')

for q in ds.queries_iter():
    ...  # q.query_id, q.query, q.subtopics (number, probability, description)
for qrel in ds.qrels_iter():
    ...  # query_id, doc_id, relevance (0-4), iteration = intent number

doc = ds.docs_store().get('clueweb09-ja0000-13-38036')
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

Two gotchas: pyndeval caps cutoffs at 20 (no `@100`), and `calc_aggregate`
averages over every topic present in the qrels — restrict the qrels to your
topic subset first, or scores are deflated.

Topics 0001–0100 in the same distribution are Chinese; they are out of scope
here.
