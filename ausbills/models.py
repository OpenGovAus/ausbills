from dataclasses import dataclass
from typing import Dict, List, NewType
import json

PdfUrl = NewType('PdfUrl', str)
UrlStr = NewType('UrlStr', str)


@dataclass
class BillMeta:
    title: str
    link: UrlStr
    parliament: str


@dataclass
class Bill:
    title: str
    link: UrlStr
    progress: Dict
    chamber_progress: int
    bill_text_links: List[Dict]

    def asDict(self) -> dict:
        return(self.__dict__)

    def asJson(self) -> str:
        return(json.dumps(self.asDict(), indent=2))
