from dataclasses import dataclass
from typing import NewType
from .types_parliament import Parliament, House

PdfUrl = NewType('PdfUrl', str)
UrlStr = NewType('UrlStr', str)

@dataclass
class BillMeta:
    parliament: Parliament
    house: House
    id: str
    title: str
    link: UrlStr


@dataclass
class Bill:
    # TODO need to expand this
    text_link: str
