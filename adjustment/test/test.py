import os
import sys

sys.path.append(
    os.path.abspath(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
)

from pathlib import Path

from pybo import *
from adjustseg import AdjustSeg

def test_tokens(adj):
    for token in adj.c_ambiguous:
        assert not token.startswith("-")

    for token in adj.c_nonambiguous:
        assert not token.startswith("-")

if __name__ == "__main__":

    path = Path(".")
    volumes = ["testcase"]

    tok = BoTokenizer('POS')
    adj = AdjustSeg(path, volumes)

    adj.stats()

    # testcase
    test_tokens(adj)

    print("Test pass.... ok")
