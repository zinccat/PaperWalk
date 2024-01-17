import requests
import backoff
from logging import (
    getLogger,
    StreamHandler,
    Formatter,
    DEBUG,
    INFO,
    WARNING,
    ERROR,
    CRITICAL,
)

logger = getLogger(__name__)
logger.setLevel(INFO)


class SemanticScholarAPI:
    def __init__(self, api_key=None):
        if api_key is not None:
            self.api_key = api_key
            self.header = {"x-api-key": self.api_key}
        else:
            self.header = None
            logger.warning("API key is not set")
        self.timeout = 10
        self.fields = (
            "title,authors,abstract,citationCount,referenceCount,externalIds,year"
        )
        self.limit = 10
        self.max_limit = 100
        assert (
            self.limit <= self.max_limit
        ), "limit must be less than or equal to max_limit"

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.Timeout, requests.exceptions.ConnectionError),
        max_tries=3,
        on_giveup=lambda x: logger.error("Failed to fetch data"),
        raise_on_giveup=False,
    )
    def _request(self, url: str) -> [dict, None]:
        response = requests.get(url, headers=self.header, timeout=self.timeout)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to fetch data")
            return None

    def fetch_paper(self, paper_id):
        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields={self.fields}&limit={self.limit}"
        return self._request(url)

    def fetch_citations(self, paper_id, fetch_all=False):
        if fetch_all:
            finished = False
            offset = 0
            while not finished:
                url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations?fields={self.fields}&limit={self.max_limit}&offset={offset}"
                response = self._request(url)
                if response is None:
                    offset += self.max_limit
                    continue
                elif len(response.get("data", [])) == 0:
                    finished = True
                else:
                    offset += self.max_limit
                    yield response
        else:
            url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations?fields={self.fields}&limit={self.limit}"
            yield self._request(url)

    def fetch_references(self, paper_id, fetch_all=False):
        if fetch_all:
            finished = False
            offset = 0
            while not finished:
                url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references?fields={self.fields}&limit={self.max_limit}&offset={offset}"
                response = self._request(url)
                if response is None:
                    offset += self.max_limit
                    continue
                elif len(response.get("data", [])) == 0:
                    finished = True
                else:
                    offset += self.max_limit
                    yield response
        else:
            url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references?fields={self.fields}&limit={self.limit}"
            yield self._request(url)


if __name__ == "__main__":
    api = SemanticScholarAPI()
    # fetch a paper
    paper = api.fetch_paper("649def34f8be52c8b66281af98ae884c09aef38b")
    print(paper)
    print(
        api.fetch_references(
            "649def34f8be52c8b66281af98ae884c09aef38b", fetch_all=False
        )
    )
    # fetch all citations of a paper
    for citation in api.fetch_references(
        "649def34f8be52c8b66281af98ae884c09aef38b", fetch_all=False
    ):
        print(citation)
