"""
Utilities for the Valtiopaivat Corpus
"""
from pyriksdagen.utils import (
    get_formatted_uuid,
    parse_tei,
    write_tei,
)
import json




def infer_metadata(filename, verbose=False):
    """
    Heuristically infer metadata from a protocol id or filename.

    Args

        filename (str): the protocols filename. Agnostic wrt. dashes and underscores. Can be relative or absolute.
        verbose (bool): print stuff

    Returns a dict with keys "filename", "doc_type", "chamber", "year", and "number"
    """
    metadata = dict()
    doc = filename.split("/")[-1].split(".")[0]
    metadata["filename"] = doc
    doctype, year, chamber, num  = doc.split("_")
    metadata["document_type"] = doctype
    if chamber == "":
        metadata["chamber"] = None
    else:
        metadata["chamber"] = chamber.capitalize()
    metadata['yearstr'] = year
    metadata["year"] = year[:4]
    if len(year) > 4:
        metadata["secondary_year"] = year[-4:]
    else:
        metadata["secondary_year"] = None
    metadata["number"] = num
    if verbose: print("INFO:\n", json.dumps(metadata, indent=2))
    return metadata


XML_NS = "{http://www.w3.org/XML/1998/namespace}"
TEI_NS = "{http://www.tei-c.org/ns/1.0}"
