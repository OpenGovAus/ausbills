from dataclasses import dataclass
from typing import NewType
from .types_parliament import Parliament, House
import json

PdfUrl = NewType('PdfUrl', str)
UrlStr = NewType('UrlStr', str)


@dataclass
class BillMeta:
    title: str
    link: UrlStr


@dataclass
class Bill:
    title: str
    link: UrlStr
    sponsor: str
    text_link: str

    def asDict(self) -> dict:
        return(self.__dict__)

    def asJson(self) -> str:
        return(json.dumps(self.asDict()))
