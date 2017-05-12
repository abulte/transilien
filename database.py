"""Database wrapper"""

import dataset
from stuf import stuf

import settings


def get():
    """Get DB connector"""
    return dataset.connect(settings.DATABASE_URI, row_type=stuf)
