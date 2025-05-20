"""
Utilities for the Valtiopaivat Corpus
"""
from lxml import etree
from pyriksdagen.utils import (
    elem_iter,
    get_formatted_uuid,
    parse_tei,

)
import json




def write_tei(elem, dest_path, padding=8) -> None:
    """
    Write a corpus document to disk.

    Args:
        elem (etree._Element): tei root element
        dest_path (str): protocol path
    """
    def _sort_attrs(elem):
        custom_order = ["xml:id", "type", "subtype"]
        attrs = sorted(elem.attrib.items())
        if len(attrs) == 0 or type(attrs) == list:
            return elem
        d = {}
        for _ in custom_order:
            if _ in attrs:
                d[_] = attrs[_]
                del attrs[_]
        for k,v in attrs.items():
            d[k] = v
        elem.attrib.clear()
        for k, v in d.items():
            elem.attrib[k] = v
        return elem

    def _iter(root, ns="{http://www.tei-c.org/ns/1.0}"):
        for body in root.findall(".//" + ns + "body"):
            for div in body.findall(ns + "div"):
                for ix, elem in enumerate(div):
                    elem = _sort_attrs(elem)
                    if elem.tag == ns + "u":
                        yield "u", elem
                    elif elem.tag == ns + "note":
                        yield "note", elem
                    elif elem.tag == ns + "pb":
                        yield "pb", elem
                    elif elem.tag == "pb":
                        elem.tag = ns + "pb"
                        yield "pb", elem
                    elif elem.tag == ns + "seg":
                        yield "seg", elem
                    elif elem.tag == "u":
                        elem.tag = ns + "u"
                        yield "u", elem
                    elif elem.tag == "p":
                        elem.tag = ns+"p"
                        yield "p", elem
                    elif elem.tag == ns + "p":
                        yield "p", elem
                    else:
                        warnings.warn(f"Unrecognized element {elem.tag}")
                        yield None

    def _format_paragraph(paragraph, spaces):
        s = "\n" + " " * spaces
        words = paragraph.replace("\n", "").strip().split()
        row = ""
        for word in words:
            if len(row) > 60:
                s += row.strip() + "\n" + " " * spaces
                row = word
            else:
                row += " " + word

        if len(row.strip()) > 0:
            s += row.strip() + "\n" + " " * (spaces - 2)
        if s.strip() == "":
            return None
        return s

    def _format_texts(root, padding=12):
        for tag, elem in _iter(root):
            if tag in ["note", "p"]:
                if type(elem.text) == str:
                    elem.text = _format_paragraph(elem.text, padding+2)
                else:
                    elem.text = None
                if elem.text == None:
                    elem.getparent().remove(elem)
            elif tag == "u":
                if len("".join(elem.itertext())) == 0:
                    elem.getparent().remove(elem)
                elif len(list(elem)) > 0:
                    # Format segs' text content
                    # Remove segs with no text content
                    for seg in elem:
                        if type(seg.text) == str:
                            seg.text = _format_paragraph(seg.text, padding+4)
                        else:
                            seg.text = None
                        if seg.text is None:
                            seg.getparent().remove(seg)
                    elem.text = None
                else:
                    elem.getparent().remove(elem)
        return root

    elem = _format_texts(elem, padding=padding)
    b = etree.tostring(
        elem,
        pretty_print=True,
        encoding="utf-8",
        xml_declaration=True
    )
    with open(dest_path, "wb") as f:
        f.write(b)


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
