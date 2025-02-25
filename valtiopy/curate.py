"""
Functions for curating the Valtiopaivat Corpus from scanned, OCRed image files
"""
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
    """
    Convert a list of alto files to a dict
    {page_index: [paragraph, paragraph, paragraph...]

    NB. There was a graphic type element in the alto xml that was causing the alto package to throw errors.
    I went into the soutce code of the package and changed the line with raise Error...
    to warnings.warn...

    Args

        files: (list) collection of alto file paths

    Return

        paragraphs (dict)
    """
    paragraphs = {}
    in_sync = True
    for file_ in files:

        nr = file_.split('-')[-1].replace('.xml', '')
        try:
            altofile = alto.parse_file(file_)
        except:
            print("OOOPS", file_)
            raise Error("sth isn't right")
        pp = _alto_extract_paragraphs(altofile)
        paragraphs[nr] = pp
    return paragraphs


def dict_to_tei(data, verbose=False):
    """
    Convert a metadata dict into a TEI XML tree

    Args

        data (dict): dictionary containing protocol level metadata
        verbose (bool): print stuff

    Return

        tei (lxml.etree.Element): the protocol as a TEI-formatted lxml tree root
    """
    if verbose: ptint(f"INFO: Preparing tei")
    metadata = copy.deepcopy(data)
    dt = {
        "prot": "records",
        "ptk": "records",
        "hand": "handlingar",
        "ask": "handlingar",
        "bil": "handlingar",
        "reg": "register",
        "sis": "register"
    }
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
    for nr, pp in data["paragraphs"].items():
        pb = etree.SubElement(body_div, "pb")
        pb.attrib["facs"] = f"https://swerik-project.github.io/valtiopaivat-{dt[metadata['document_type']]}-pdf/{metadata['yearstr']}/{metadata['filename']}-{nr}.pdf"
        for paragraph in pp:
            if metadata["document_type"] in ["ptk", "prot"]:
                elem = etree.SubElement(body_div, "note")
            else:
                elem = etree.SubElement(body_div, "p")
            elem.text = paragraph
            element_seed += paragraph
            elem.attrib[f"{XML_NS}id"] = get_formatted_uuid(element_seed)

    return tei



def dict_to_parlaclarin(data, tei_loc, verbose=False):
    """
    Create per-protocol parlaclarin files of all files provided in file_db.
    Does not return anything, instead writes the data on disk.

    Args:

        data (dict): metadata and data
        tei_loc (str): path to tei
        verbose (bool): print stuff
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
