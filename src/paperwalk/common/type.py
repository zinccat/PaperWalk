from typing import List, Optional, Tuple, Union
from enum import Enum
from pydantic import BaseModel


class Relation(Enum):
    CITES = 1
    REFERENCES = 2


class Paper(BaseModel):
    def __init__(
        self,
        paper_id: str,
        title: str,
        first_author: str,
        first_author_id: str,
        last_author: str,
        last_author_id: str,
        abstract: str,
        citation_count: int,
        reference_count: int,
        arxiv: str,
        year: int,
    ):
        self.paper_id = paper_id
        self.title = title
        self.first_author = first_author
        self.first_author_id = first_author_id
        self.last_author = last_author
        self.last_author_id = last_author_id
        self.abstract = abstract
        self.citation_count = citation_count
        self.reference_count = reference_count
        self.arxiv = arxiv
        self.year = year
