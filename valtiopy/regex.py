import os
import regex as re

def compile_pattern(query):
    """
    load query from a file

    Args

        query (str): name of .rq file stored with this module under `regex/`
    """
    if not os.path.exists(f"{os.path.dirname(os.path.abspath(__file__))}/rq/{query}.rq"):
        raise FileNotFoundError(f"Couldn't find file : {os.path.dirname(os.path.abspath(__file__))}/rq/{query}.rq")

    with open(f"{os.path.dirname(os.path.abspath(__file__))}/rq/{query}.rq", 'r') as inf:
        lines = [rf"{_.strip()}" for _ in inf.readlines()]
    q = ''.join(lines)
    #q = q.replace("\\s", r"\s")
    q = q.replace("\\\\","\\")
    print(q)
    pat =  re.compile(rf"{q}")
    print(pat)
    return pat
