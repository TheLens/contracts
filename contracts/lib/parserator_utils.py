"""
A few utility functions to support the web app
"""
import json
import logging
from flask import request
from pythondocumentcloud import DocumentCloud
from contracts import TAGS_URL
from contract_parser import tokenize

logging.basicConfig(level=logging.DEBUG, filename="parserator.log")
CLIENT = DocumentCloud()


def get_colors(tag):
    """
    Get the colors for a certain tag
    """

    with open(TAGS_URL) as data_file:
        data = json.load(data_file)
    return [d for d in data if d['name'] == tag].pop()


def sort_keys(keys):
    """
    Keys come in the form page#-tokennumber (on a page)
    Sort them in order of pages, then in order of token #
    """
    keys.sort(key=lambda x: int(x.split("-")[1]))
    keys.sort(key=lambda x: int(x.split("-")[0]))
    return keys


def get_document_page(doc_cloud_id, page):
    """
    Get a page in a document cloud document
    """
    doc = CLIENT.documents.get(doc_cloud_id)
    page_text = doc.get_page_text(page)
    page_text = page_text.decode("ascii", "ignore").encode("ascii", "ignore")
    return page_text


# TO DO JINJA TEMPLATE
def span_wrap(text, span_id, tag):
    """
    Wrap a token in a span tag
    """
    if tag == "skip":
        return "<span id=\"" + span_id +\
          "\" class=\"token\" data-tag=\"" + tag + "\">" + text + "</span>"
    else:
        colors = get_colors(tag)
        style = 'style="border: 2px solid rgb(' + str(colors['red']) + ',' +\
            ' ' + str(colors['green']) + ', ' + str(colors['blue']) + ');"'
        return "<span id=\"" + span_id +\
               "\" class=\"token\" data-tag=\"" +\
               tag + "\"" + style +\
               ">" + text + "</span>"


def get_labels():
    """
    Labeled tokens come back from the UI as JSON.
    This method pulls them from the json and dumps
    them out as tuples: (text, value) ex ("1.2 Million", contract_amount)
    """
    json_request = request.json  # get the json from the server
    keys = sort_keys(json_request.keys())  # sort the keys (i.e. the token ids)
    labels = []
    for k in keys:
        # get the labels that the user input to the UI
        val = (json_request[k]['text'], json_request[k]['value'])
        labels.append(val)
    return labels


def spanify(page_text, page_no, labels=None):
    """
    Take a page of text and wrap it in span tags
    If the labels from parserator are provided.
    Otherwise it defaults to skip
    """
    tokens = tokenize(page_text, True)
    last_index_mem = 0
    in_between = ""
    new_tokens = []
    in_betweens = []
    token_no = 1
    for token in tokens:
        start = token[0]
        end = token[1]
        token_no = token_no + 1
        if last_index_mem > 0:
            in_between = page_text[last_index_mem: start]
        last_index_mem = end
        spanid = str(page_no) + "-" + str(token_no)
        if labels:
            try:
                correct_label = [l for l\
                 in labels if spanid == l['id']].pop()['label']
            except IndexError:
                logging.debug("Skipping. Could not find label for " + spanid)
                correct_label = "skip"
            new_token = span_wrap(str(page_text[start: end]), spanid, correct_label)
        else:
            new_token = span_wrap(str(page_text[start: end]), spanid, "skip")
        new_tokens.append(new_token)
        in_betweens.append(in_between)

    output = ""

    for i in range(0, len(new_tokens)):
        output = output + new_tokens[i] + in_betweens[i]

    return output.replace("\n", "<br />")
