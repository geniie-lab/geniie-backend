"""Register the NTCIR-9 INTENT-1 Japanese Document Ranking collection with
ir_datasets under the ID 'ntcir9-intent1-ja'.

Expected files in ~/.ir_datasets/ntcir9-intent1-ja/ (from the INTENT-1
research-purpose data distributed by NII/IDR):
  - ntcir9intent.0101-0200.full.xml   (100 Japanese topics with intents)
  - ntcir9intent.0101-0200.dr.Dqrels  (per-intent graded relevance, L0-L4)

Queries carry their intents as subtopics (number, probability, description).
Qrels use the intent number in the iteration field, so per-intent evaluation
(alpha-nDCG, D#-nDCG and the like) can be computed. Documents are
clueweb09-ja* ids; the ClueWeb09-JA corpus is licensed separately from CMU.
"""

import re
import xml.etree.ElementTree as ET
from typing import NamedTuple, Tuple

import ir_datasets
from ir_datasets.datasets.base import Dataset
from ir_datasets.formats import BaseQueries, BaseQrels
from ir_datasets.formats.trec import TrecQrel

NAME = 'ntcir9-intent1-ja'
TOPICS_FILE = 'ntcir9intent.0101-0200.full.xml'
QRELS_FILE = 'ntcir9intent.0101-0200.dr.Dqrels'

QREL_DEFS = {
    0: 'L0: not relevant to the intent',
    1: 'L1',
    2: 'L2',
    3: 'L3',
    4: 'L4: highly relevant to the intent',
}


class IntentSubtopic(NamedTuple):
    number: str
    probability: float
    description: str


class IntentQuery(NamedTuple):
    query_id: str
    query: str
    subtopics: Tuple[IntentSubtopic, ...]


def _parse_topics(path):
    # The XML declares an internal DTD; ElementTree parses it fine.
    root = ET.parse(path).getroot()
    for topic in root.iter('topic'):
        query_el = topic.find('query')
        subtopics = []
        for intent in topic.iter('intent'):
            desc_el = intent.find('description')
            desc = (desc_el.text or '').strip() if desc_el is not None else (intent.text or '').strip()
            subtopics.append(IntentSubtopic(
                number=intent.get('number'),
                probability=float(intent.get('probability', 'nan')),
                description=desc,
            ))
        yield IntentQuery(
            query_id=topic.get('number'),
            query=(query_el.text or '').strip() if query_el is not None else '',
            subtopics=tuple(subtopics),
        )


class IntentQueries(BaseQueries):
    def __init__(self, path):
        self._path = path

    def queries_iter(self):
        yield from _parse_topics(self._path)

    def queries_cls(self):
        return IntentQuery

    def queries_lang(self):
        return 'ja'


class IntentQrels(BaseQrels):
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
        IntentQueries(base_path / TOPICS_FILE),
        IntentQrels(base_path / QRELS_FILE),
    )
    ir_datasets.registry.register(NAME, dataset)
    return dataset


_init()
