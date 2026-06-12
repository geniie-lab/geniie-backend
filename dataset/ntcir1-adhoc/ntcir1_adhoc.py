import os
import ir_datasets
from ir_datasets.formats import JsonlDocs, TrecQueries, TrecQrels
from ir_datasets.datasets.base import Dataset, YamlDocumentation

# A unique identifier for this dataset. To avoid name conflicts, consider prefixing
# identifiers with a person/org, as done here:
NAME = 'ntcir1-adhoc'

# What to the relevance levels in qrels mean?
QREL_DEFS_TRAIN = {
    2: 'relevant',
    1: 'partially relevant',
    0: 'not relevant',
}

def _init():
    # where the content is cached
    base_path = ir_datasets.util.home_path() / NAME
    
    # Specify where to find the content. Here it's just from the repository, but it could be anywhere.
    TC_ROOT = os.path.join(os.getcwd())
    DL_DOCS = ir_datasets.util.LocalDownload(os.path.join(TC_ROOT, 'ntc1-j1.utf8.jsonl'))
    DL_QUERIES = ir_datasets.util.LocalDownload(os.path.join(TC_ROOT, 'topic0001-0083.utf8.trec'))
    DL_QRELS = ir_datasets.util.LocalDownload(os.path.join(TC_ROOT, 'rel2_ntc1-j1_0001-0083.utf8.tsv'))

    # Register the dataset with ir_datasets
    documentation = YamlDocumentation(f'{NAME}.yaml')
    base = Dataset(
        documentation('_'),
        JsonlDocs(ir_datasets.util.Cache(DL_DOCS, base_path/'ntc1-j1.utf8.jsonl')),
        TrecQueries(ir_datasets.util.Cache(DL_QUERIES, base_path/'topic0001-0083.utf8.trec')),
        TrecQrels(ir_datasets.util.Cache(DL_QRELS, base_path/'rel2_ntc1-j1_0001-0083.utf8.tsv'), QREL_DEFS_TRAIN),
    )
    ir_datasets.registry.register(f'{NAME}', base)
    
    return base

base = _init()