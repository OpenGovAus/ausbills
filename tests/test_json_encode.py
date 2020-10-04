from bs4 import BeautifulSoup
from ausbills.json_encoder import *
from tests.utils import read_data

log = get_logger(__file__)

be4_obj = BeautifulSoup(read_data("test_read_snd_and_hansard_tr_1.txt"), 'lxml')
lots_of_tags = list(be4_obj.find_all())


def test_json_encode():
    dumped = json.dumps(lots_of_tags[0], cls=AusBillsJsonEncoder)
    # log.warning(dumped)
    assert len(dumped) > 0
    loaded = json.loads(dumped)
    assert '$bs4.tag' in loaded
    bs4_tag = loaded['$bs4.tag']
    assert '$bytes' in bs4_tag
    assert len(bs4_tag['$bytes']) > 50
