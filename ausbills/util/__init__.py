import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from ..log import get_logger


class BillExtractor(object):

    logger = get_logger(__file__)

    def _download_page(self, url, postdata={}, method='GET', verify=True):
        if method == 'GET':
            return requests.get(url).text
        elif method == 'POST':
            return requests.post(url, data=postdata, verify=verify).text
        else:
            raise self.ExtractorError(
                "Invalid request method used, requires 'GET' or 'POST'")

    def _download_json(self, url, postdata={}, method='GET', verify=True):
        page_content = self._download_page(
            url, method=method, postdata=postdata, verify=verify)
        try:
            return json.loads(page_content)
        except Exception as e:
            self.logger.error('Could not encode JSON; ' + str(e))

    def _download_html(self, url, postdata={}, method='GET', verify=True):
        page_content = self._download_page(
            url, method=method, postdata=postdata, verify=verify)
        try:
            return BeautifulSoup(page_content, 'lxml')
        except Exception as e:
            self.logger.error('Could not parse page with bs4; ' + str(e))

    def _get_timestamp(self, text, pattern):
        return int(datetime.strptime(text, pattern).timestamp())

    def _get_epoch(self):
        return int(datetime.now().timestamp())

    class ExtractorError(Exception):
        pass


class BillListExtractor(BillExtractor):
    pass
