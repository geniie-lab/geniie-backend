"""Register the TREC Web Track diversity task qrels (2009-2012) with
ir_datasets under the IDs 'trec-web-<year>-diversity'.

ir_datasets already ships the topics (with subtopics) for
clueweb09/en/trec-web-2009..2012, but exposes the ad-hoc judgments only.
These datasets reuse those topics and attach the official per-subtopic
diversity qrels from trec.nist.gov, with the subtopic number in the
iteration field.

Expected files in ~/.ir_datasets/trec-web-diversity/ (from
https://trec.nist.gov/data/webmain.html, per-year data pages):
  - 2009.qrels.diversity.gz        (web/09/qrels.diversity.gz)
  - 2010.10.diversity-qrels.final  (web/10/10.diversity-qrels.final)
  - 2011.qrels.diversity           (web/11/qrels.diversity)
  - 2012.qrels.diversity           (web/12/qrels.diversity)

Notes: the 2010 file lists relevant pairs only (absent pairs are
nonrelevant, per ndeval convention); 2011/2012 use -2 for spam.
"""

import gzip

import ir_datasets
from ir_datasets.datasets.base import Dataset
from ir_datasets.formats import BaseQueries, BaseQrels
from ir_datasets.formats.trec import TrecQrel

YEARS = {
    2009: '2009.qrels.diversity.gz',
    2010: '2010.10.diversity-qrels.final',
    2011: '2011.qrels.diversity',
    2012: '2012.qrels.diversity',
}

QREL_DEFS = {
    -2: 'spam (2011-2012)',
    0: 'not relevant to the subtopic',
    1: 'relevant to the subtopic',
    2: 'relevant (graded, 2011-2012)',
    3: 'relevant (graded, 2011-2012)',
    4: 'relevant (graded, 2012)',
}


class ProxyQueries(BaseQueries):
    """Reuse the topics of an already-registered ir_datasets dataset."""

    def __init__(self, base_id):
        self._base_id = base_id

    def _base(self):
        return ir_datasets.load(self._base_id)

    def queries_iter(self):
        yield from self._base().queries_iter()

    def queries_cls(self):
        return self._base().queries_cls()

    def queries_lang(self):
        return 'en'


class DiversityQrels(BaseQrels):
    def __init__(self, path):
        self._path = path

    def qrels_iter(self):
        # Lines: <topic> <subtopic> <docno> <judgment>
        opener = gzip.open if str(self._path).endswith('.gz') else open
        with opener(self._path, 'rt', encoding='utf-8', errors='replace') as f:
            for line in f:
                parts = line.split()
                if len(parts) != 4:
                    continue
                topic, subtopic, docno, judgment = parts
                yield TrecQrel(query_id=topic, doc_id=docno,
                               relevance=int(judgment), iteration=subtopic)

    def qrels_cls(self):
        return TrecQrel

    def qrels_defs(self):
        return QREL_DEFS


def _init():
    base_path = ir_datasets.util.home_path() / 'trec-web-diversity'
    for year, filename in YEARS.items():
        name = f'trec-web-{year}-diversity'
        if name in ir_datasets.registry:
            continue
        ir_datasets.registry.register(name, Dataset(
            ProxyQueries(f'clueweb09/en/trec-web-{year}'),
            DiversityQrels(base_path / filename),
        ))


_init()
