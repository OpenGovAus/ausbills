from dataclasses import dataclass
from typing import NewType
from .types_parliament import Parliament, House
import json

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
    summary: str

    def asDict(self) -> dict:
        return(self.__dict__)

    def asJson(self) -> str:
        return(json.dumps(self.asDict()))
