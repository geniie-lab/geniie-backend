"""Register the NTCIR-9 INTENT-1 Japanese Document Ranking collection with
ir_datasets under the ID 'ntcir9-intent1-ja'.

Expected files in ~/.ir_datasets/ntcir9-intent1-ja/ (from the INTENT-1
research-purpose data distributed by NII/IDR):
  - ntcir9intent.0101-0200.full.xml   (100 Japanese topics with intents)
  - ntcir9intent.0101-0200.dr.Dqrels  (per-intent graded relevance, L0-L4)

Queries carry their intents as subtopics (number, probability, description).
Qrels use the intent number in the iteration field, so per-intent evaluation
(alpha-nDCG, D#-nDCG and the like) can be computed.

Documents are proxied from ir_datasets' built-in 'clueweb09/ja' (all
clueweb09-ja* ids), so docs_iter()/docs_store() work on this dataset
directly. That requires the ClueWeb09-JA corpus (licensed separately from
CMU) unpacked where the built-in expects it:
  ~/.ir_datasets/clueweb09/corpus/ClueWeb09_Japanese_{1,2}/
  ~/.ir_datasets/clueweb09/corpus/record_counts/ClueWeb09_Japanese_{1,2}_counts.txt
Note the CMU download script writes these under a ClueWeb09-NTCIR-Intent/
subdirectory; move them up a level. Doc bodies are raw HTML *bytes* (often
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

DOCS_ID = 'clueweb09/ja'

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
        ProxyDocs(DOCS_ID),
        IntentQueries(base_path / TOPICS_FILE),
        IntentQrels(base_path / QRELS_FILE),
    )
    ir_datasets.registry.register(NAME, dataset)
    return dataset


_init()
