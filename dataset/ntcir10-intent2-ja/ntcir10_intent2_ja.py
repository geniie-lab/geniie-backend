"""Register the NTCIR-10 INTENT-2 Japanese Document Ranking collection with
ir_datasets under the ID 'ntcir10-intent2-ja'.

Expected files in ~/.ir_datasets/ntcir10-intent2-ja/ (from the INTENT-2
research-purpose data distributed by NII/IDR):
  - ntcir10intent.0301-0400.full-revised.xml  (100 Japanese topics with
    fac/amb/nav topic tags and nav/inf intent tags)
  - INTENT-2DRJ.Dqrels                        (per-intent graded relevance, L0-L4)
  - INTENT-2DRJ.5-4.DINprob                   (intent probabilities with
    nav/inf type labels; merged into subtopics when present)

Queries carry their intents as subtopics (number, probability, intent type,
description); the topic-level fac/amb/nav tag is exposed as query type.
Qrels use the intent number in the iteration field.

Documents are proxied from ir_datasets' built-in 'clueweb09/ja' (all
clueweb09-ja* ids), so docs_iter()/docs_store() work on this dataset
directly. That requires the ClueWeb09-JA corpus (licensed separately from
CMU) unpacked where the built-in expects it:
  ~/.ir_datasets/clueweb09/corpus/ClueWeb09_Japanese_{1,2}/
  ~/.ir_datasets/clueweb09/corpus/record_counts/ClueWeb09_Japanese_{1,2}_counts.txt
Doc bodies are raw HTML *bytes* (often
Shift_JIS); use default_text() for decoded text, whose first line is the
HTML title.
"""

import re
import xml.etree.ElementTree as ET
from typing import NamedTuple, Tuple

import ir_datasets
from ir_datasets.datasets.base import Dataset
from ir_datasets.formats import BaseDocs, BaseQueries, BaseQrels
from ir_datasets.formats.trec import TrecQrel

NAME = 'ntcir10-intent2-ja'
DOCS_ID = 'clueweb09/ja'
TOPICS_FILE = 'ntcir10intent.0301-0400.full-revised.xml'
QRELS_FILE = 'INTENT-2DRJ.Dqrels'
DINPROB_FILE = 'INTENT-2DRJ.5-4.DINprob'

QREL_DEFS = {
    0: 'L0: not relevant to the intent',
    1: 'L1',
    2: 'L2',
    3: 'L3',
    4: 'L4: highly relevant to the intent',
}


class Intent2Subtopic(NamedTuple):
    number: str
    probability: float
    intent_type: str  # 'nav', 'inf', or '' when unknown
    description: str


class Intent2Query(NamedTuple):
    query_id: str
    query: str
    type: str  # 'fac', 'amb', 'nav', or '' when untagged
    subtopics: Tuple[Intent2Subtopic, ...]


def _load_dinprob(path):
    # Lines: <topic> <intent> <probability> <nav|inf>
    types = {}
    if not path.exists():
        return types
    with open(path, encoding='utf-8') as f:
        for line in f:
            parts = line.split()
            if len(parts) == 4:
                types[(parts[0], parts[1])] = parts[3]
    return types


def _parse_topics(path, intent_types):
    root = ET.parse(path).getroot()
    for topic in root.iter('topic'):
        query_el = topic.find('query')
        topic_id = topic.get('number')
        subtopics = []
        for intent in topic.iter('intent'):
            desc_el = intent.find('description')
            desc = (desc_el.text or '').strip() if desc_el is not None else (intent.text or '').strip()
            number = intent.get('number')
            itype = intent.get('type') or intent_types.get((topic_id, number), '')
            subtopics.append(Intent2Subtopic(
                number=number,
                probability=float(intent.get('probability', 'nan')),
                intent_type=itype,
                description=desc,
            ))
        yield Intent2Query(
            query_id=topic_id,
            query=(query_el.text or '').strip() if query_el is not None else '',
            type=topic.get('type', '') or '',
            subtopics=tuple(subtopics),
        )


class ProxyDocs(BaseDocs):
    """Reuse the documents of an already-registered ir_datasets dataset."""

    def __init__(self, base_id):
        self._base_id = base_id

    def _base(self):
        return ir_datasets.load(self._base_id)

    def docs_iter(self):
        return self._base().docs_iter()

    def docs_cls(self):
        return self._base().docs_cls()

    def docs_store(self):
        # WarcDocs.docs_store() takes no field argument.
        return self._base().docs_store()

    def docs_count(self):
        return self._base().docs_count()

    def docs_namespace(self):
        return self._base().docs_namespace()

    def docs_lang(self):
        return self._base().docs_lang()


class Intent2Queries(BaseQueries):
    def __init__(self, path, dinprob_path):
        self._path = path
        self._dinprob_path = dinprob_path

    def queries_iter(self):
        yield from _parse_topics(self._path, _load_dinprob(self._dinprob_path))

    def queries_cls(self):
        return Intent2Query

    def queries_lang(self):
        return 'ja'


class Intent2Qrels(BaseQrels):
    def __init__(self, path):
        self._path = path

    def qrels_iter(self):
        # Lines: <topic> <intent> <docid> L<grade>
        with open(self._path, encoding='utf-8') as f:
            for line in f:
                parts = line.split()
                if len(parts) != 4:
                    continue
                topic, intent, docid, grade = parts
                m = re.fullmatch(r'L(\d+)', grade)
                if not m:
                    continue
                yield TrecQrel(query_id=topic, doc_id=docid,
                               relevance=int(m.group(1)), iteration=intent)

    def qrels_cls(self):
        return TrecQrel

    def qrels_defs(self):
        return QREL_DEFS


def _init():
    if NAME in ir_datasets.registry:
        return ir_datasets.load(NAME)
    base_path = ir_datasets.util.home_path() / NAME
    dataset = Dataset(
        ProxyDocs(DOCS_ID),
        Intent2Queries(base_path / TOPICS_FILE, base_path / DINPROB_FILE),
        Intent2Qrels(base_path / QRELS_FILE),
    )
    ir_datasets.registry.register(NAME, dataset)
    return dataset


_init()
