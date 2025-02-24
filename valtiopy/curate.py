from lxml import etree
from pyparlaclarin.create import pc_header
from pyriksdagen.download import _alto_extract_paragraphs
from valtiopy.utils import (
    get_formatted_uuid,
    parse_tei,
    TEI_NS,
    write_tei,
    XML_NS,
)
import alto
import copy
import os


def convert_alto(files):
    paragraphs = []
    in_sync = True
    for file_ in files:
        altofile = alto.parse_file(file_)
        paragraphs += _alto_extract_paragraphs(altofile)
    return paragraphs


def dict_to_tei(data, verbose=False):
    """
    Convert a metadata dict into a TEI XML tree

    Args:
        data (dict): dictionary containing protocol level metadata

    Returns:
        tei (lxml.etree.Element): the protocol as a TEI-formatted lxml tree root
    """
    if verbose: ptint(f"INFO: Preparing tei")
    metadata = copy.deepcopy(data)

    nsmap = {None: TEI_NS}
    nsmap = {key: value.replace("{", "").replace("}", "") for key,value in nsmap.items()}
    tei = etree.Element("TEI", nsmap=nsmap)
    #protocol_id = metadata["protocol_id"]
    metadata["document_title"] = (
        f"Finnish parliamentary document: {metadata['document_type']} {metadata['yearstr']}, {metadata['chamber']} number {metadata['number']}"
    )
    documentHeader = pc_header(metadata)
    tei.append(documentHeader)

    text = etree.SubElement(tei, "text")
    front = etree.SubElement(text, "front")
    preface = etree.SubElement(front, "div", type="preface")
    etree.SubElement(preface, "head").text = metadata["filename"]
    if "date" not in metadata:
        year = metadata.get("year", 2020)
        metadata["date"] = str(year) + "-01-01"

    etree.SubElement(preface, "docDate", when=metadata["date"]).text = metadata.get(
        "date", "2020-01-01"
    )

    body = etree.SubElement(text, "body")
    body_div = etree.SubElement(body, "div")

    protocol_id = metadata["filename"]
    element_seed = f"{protocol_id}\nNA\n"
    print(element_seed)
    for paragraph in data["paragraphs"]:
        if type(paragraph) == int:
            element_seed = f"{protocol_id}\n{paragraph}\n"
            pb = etree.SubElement(body_div, "pb")
            sitting, number = metadata["sitting"], metadata["number"]
            #paragraph = f"{paragraph:03d}"
            #link = f"https://betalab.kb.se/prot-{sitting}--{number}/prot_{sitting}__{number}-{paragraph}.jp2/_view"
            #pb.attrib["facs"] = link
        else:
            note = etree.SubElement(body_div, "note")
            note.text = paragraph
            element_seed += paragraph
            note.attrib[f"{XML_NS}id"] = get_formatted_uuid(element_seed)

    return tei



def dict_to_parlaclarin(data, tei_loc, verbose=False):
    """
    Create per-protocol parlaclarin files of all files provided in file_db.
    Does not return anything, instead writes the data on disk.

    Args:
        data (dict): metadata and data

    Returns:
        None
    """
    parlaclarin_path = f"{tei_loc}/{data['filename']}.xml"
    if verbose: print(f"INFO: preparing to write tei to {parlaclarin_path}")
    tei = dict_to_tei(data)
    if verbose: print("INFO: TEI OK... write and read-write test")
    os.makedirs(tei_loc, exist_ok=True)
    write_tei(tei, parlaclarin_path)
    root, ns = parse_tei(parlaclarin_path)
    write_tei(root, parlaclarin_path)
    if verbose: print("INFO:    OK")
