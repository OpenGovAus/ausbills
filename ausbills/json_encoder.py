import base64
import json
from datetime import datetime

from bs4 import Tag
from pymonad.maybe import Maybe
from dataclasses import is_dataclass

from .log import get_logger
from .types import House

json_d = json.JSONEncoder.default
log = get_logger(__file__)


class AusBillsJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Maybe):
            return {"$nothing": None} if \
                obj.is_nothing() else {"$just": obj.value}
        if isinstance(obj, Tag):
            return {"$bs4.tag": obj.encode()}
        if isinstance(obj, bytes):
            return {"$bytes": base64.encodebytes(obj).decode()}
        if is_dataclass(obj):
            return dict(**obj.__dict__)
        if isinstance(obj, House):
            return {"$house": obj.value}
        if isinstance(obj, datetime):
            return {"$dateIso8601": obj.isoformat()}
        log.warning("Got something of unexpected type"
                    "({}\n\nObj: {}\n\ndir: {}"
                    .format(type(obj), str(obj), dir(obj)))

        return json_d(self, obj)
