
'''docstring'''

import json
import sys
import importlib

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from pythondocumentcloud import DocumentCloud
from contracts.lib.parserator_utils import sort_keys

MODULE = importlib.import_module('parser')
client = DocumentCloud()


def tokenize(doc_cloud_id):
    """
    Breaks a document into tokens based on the module's tokenizer.
    """

    ids = {}
    document = client.documents.get(doc_cloud_id)
    pages = document.pages
    for page in range(1, pages + 1):
        counter = 0
        tokens = MODULE.tokenize(document.get_page_text(page))
        for t in tokens:
            tokenid = str(page) + "-" + str(counter)
            counter += 1
            output = {}
            output['page'] = page
            output['word'] = t
            output['count'] = counter
            ids[tokenid] = output
    return ids


def parse(doc_cloud_id):
    doc = client.documents.get(doc_cloud_id)
    full_text = doc.full_text
    return MODULE.parse(full_text)


def pre_process(doc_cloud_id):
    tokens = tokenize(doc_cloud_id)
    tags = MODULE.parse(client.documents.get(doc_cloud_id).full_text)
    token_ids = sort_keys(tokens.keys())
    out = []
    for number in range(0, len(tags)):
        tag = tags[number]
        token = tokens[token_ids[number]]
        token['label'] = tag[1]  # add the tag label to the token
        token['id'] = token_ids[number]
        assert token['word'] == tag[0]
        out.append(token)
    return out


doc_cloud_id = sys.argv[1]

parsed = pre_process(doc_cloud_id)

conn = S3Connection()
bucket = conn.get_bucket('lensnola')
k = Key(bucket)
k.key = 'contracts/contract_amounts/computer_labels/' + doc_cloud_id

k.set_contents_from_string(json.dumps(parsed))
