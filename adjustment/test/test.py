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

if __name__ == "__main__":
    path = Path('../../kt-no-tantra')

    volumes = [
        '100 དབུ་མ། ཞ_cleaned_cleaned_cleaned.txt',
        '001_cleaned_cleaned_cleaned.txt',
        '044_cleaned_cleaned_cleaned.txt'
    ]

    tok = BoTokenizer('POS')
    adj = AdjustSeg(path, volumes)

    adj.stats()
