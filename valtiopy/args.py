"""
A DRY argparse helper for common arguments
"""
from glob import glob
from valtiopy.config import (
    create_new_config,
    load_config,
)
import argparse
import warnings




class NotImplemented(Warning):
    """
    Warn on unimplemented functions
    """
    def __init__(self, func):
        self.message = f"\n    --~~--~~>    The function {func} is not implemented yet."

    def __str__(self):
        return self.message


def custom_serializer(obj):
    """
    This takes an argparse args class and either serializes it to txt,
    or replaces a non-serializable object with its name.

    used for debugging the argparse args
    """
    try:
        return json.JSONEncoder().default(obj)
    except TypeError:
        return f"Non-serializable: {type(obj).__name__}"


def populate_common_args(parser):
    """
    Add common arguments to a parser that will be used in most of the scripts.

    Args

        parser: argparse parser instance

    Returns

        parser
    """
    parser.add_argument("-c", "--config-name",
                        default = 'default',
                        help = "Load a config file created with the valtiopy.config module or tracked with it by name")
    parser.add_argument("--config-path",
                        default = None,
                        help = "Point to a config file to load.")
    parser.add_argument("--config-create",
                        action = 'store_true',
                        help = "Create a new config. The config name and config path arguments must be set with this option.")
    parser.add_argument("-s", "--start",
                        type = str,
                        help = "year to start processing")
    parser.add_argument("-e", "--end",
                        type = str,
                        help = "year to end processing")
    parser.add_argument("-m", "--meeting",
                        type = str,
                        help = "A particular meeting year or riksmöte (either a year or range when a given parliament was active).")
    parser.add_argument("-l", "--languages",
                        choices = ["f", "s", "fs"],
                        nargs= "+",
                        default = ['s'],
                        help = "Parse documents with the selected primary languages")
    parser.add_argument("-k", "--chambers",
                        choices = ["adeln", "borgare", "praster", "talonpajat", "papisto", "porvaristo"],
                        nargs = "+",
                        help = "Parse documents from chambers.")
    parser.add_argument("-d", "--doctypes",
                        choices = ["ask", "hand", "prot", "ptk", "bil", "reg", "sis"],
                        nargs = "+",
                        help = "Document types to process")
    parser.add_argument("-f", "--docformats",
                        choices = ["alto", "tei", "pdf"],
                        default = ['tei'],
                        nargs = "+",
                        help = "Which kind of documents do you want to call up?")
    parser.add_argument("-v", "--verbose",
                        action = 'store_true',
                        help = "Print extra information about what's going on")
    return parser


def fetch_parser(description=None):
    """
    Create a parser instance and populate it with common arguments.

    Args

        description (str): description of script calling parser (__doc__)

    Returns

        parser
    """
    parser = argparse.ArgumentParser(description=description)
    parser = populate_common_args(parser)
    return parser


def impute_arg_values(args):
    """
    parse common arguments and pre-handle args for the script user

    Args

        args: Argparse argument class instances

    Returns

        args
    """
    def _handle_config(args):
        """
        fetch or create configif args.verbose: print(f"INFO:
        """
        if args.config_create:
            if args.verbose: print(f"INFO: Creating a new config file called \"{args.config_name}\" at {args.config_path}")
            args.config = create_new_config(name=args.config_name, location=args.config_path)
        else:
            if args.config_path is not None:
                if args.verbose: print(f"INFO: Loading config from path {args.config_path}")
                args.config = load_config(location=args.config_path)
            else:
                if args.verbose: print(f"INFO: Loading config from name {args.config_name}")
                args.config = load_config(name=args.config_name)
        return args

    def _fetch_documents(args):
        """
        fetch documents according to start/end or meeting time frame

        Args

            args: Argparse argument class instances

        Returns

            args
        """
        def _get_files(paths, args, ext=".xml"):
            files = []
            for path_ in paths:
                if args.verbose: print(f"INFO: looking for files at {path_}")
                if args.meeting is not None:
                    if args.verbose: print(f"INFO: riksmöte meeting specified {args.meeting}")
                    fs = sorted(glob(f"{path_}/data/{args.meeting}/**/*{ext}", recursive=True))
                    files.extend(fs)
                    if args.verbose: print(f"INFO:   found {len(fs)} files")
                else:
                    fs = sorted(glob(f"{path_}/data/**/*{ext}", recursive=True))
                    if args.verbose: print(f"INFO: found {len(fs)} files")
                    if args.start is not None:
                        if args.verbose: print(f"INFO:    filtering for start ({args.start}) and end ({args.end})")
                        fs = [f for f in fs if int(f.split('/')[-1].split('_')[1][:4]) >= int(args.start)]
                        fs = [f for f in fs if int(f.split('/')[-1].split('_')[1][-4:]) <= int(args.end)]
                        if args.verbose: print(f"INFO:    {len(fs)} files leftover")
                    files.extend(fs)
            return files

        for format in args.docformats:
            if format == 'alto':
                if args.verbose: print("INFO: Looking for ALTO files")
                paths = list({k:v for k,v in vars(args.config).items() if "ALTO" in k and v is not None}.values())
                args.alto_files = _get_files(paths, args)
                if args.verbose: print(f"INFO:    found {len(args.alto_files)} alto files")
            elif format == 'pdf':
                if args.verbose: print("INFO: Looking for PDF files")
                paths = list({k:v for k,v in vars(args.config).items() if "PDF" in k and v is not None}.values())
                args.pdf_files = _get_files(paths, args, ext=".pdf")
                if args.verbose: print(f"INFO:    found {len(args.pdf_files)} pdf files")
            elif format == 'tei':
                if args.verbose: print("INFO: Looking for TEI files")
                paths = list({k:v for k,v in vars(args.config).items() if "TEI" in k and v is not None}.values())
                args.tei_files = _get_files(paths, args)
                if args.verbose: print(f"INFO:    found {len(args.tei_files)} tei files")
        return args

    def _filter_doctype(args):
        """
        select documents based on doctype

        Args

            args: Argparse argument class instances

        Returns

            args
        """
        if args.doctypes is None:
            return args
        if args.verbose: print(f"INFO: filtering docs for type {args.doctypes}")
        for format in args.docformats:
            if hasattr(args, f"{format}_files"):
                files = getattr(args, f"{format}_files")
                if args.verbose: print(f"INFO:     starting with {len(files)} {format} files")
                files = [f for f in files if f.split('/')[-1].split('_')[0] in args.doctypes]
                if args.verbose: print(f"INFO:    --->  {len(files)} leftover")
                setattr(args, f"{format}_files", files)
        return args

    def _filter_language(args):
        """
        select documents based on the primary language

        Args

            args: Argparse argument class instances

        Returns

            args
        """
        warnings.warn(_filter_language.__name__, NotImplemented)
        return args

    def _filter_chamber(args):
        """
        select documents based on the chamber

        Args

            args: Argparse argument class instances

        Returns

            args
        """
        if args.chambers is None:
            return args
        if args.verbose: print(f"INFO: filtering docs for chamber {args.chambers}")
        for format in args.docformats:
            if hasattr(args, f"{format}_files"):
                files = getattr(args, f"{format}_files")
                if args.verbose: print(f"INFO:     starting with {len(files)} {format} files")
                files = [f for f in files if f.split('/')[-1].split('_')[2] in args.chambers]
                if args.verbose: print(f"INFO:    --->  {len(files)} leftover")
                setattr(args, f"{format}_files", files)
        return args

    args = _handle_config(args)
    args = _fetch_documents(args)
    args = _filter_doctype(args)
    args = _filter_language(args)
    args = _filter_chamber(args)

    return args
