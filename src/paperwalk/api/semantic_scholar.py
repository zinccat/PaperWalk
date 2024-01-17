import requests

class SemanticScholarAPI:

    def __init__(self, api_key=None):
        if api_key is not None:
            self.api_key = api_key
            self.header = {
                "x-api-key": self.api_key
            }
        else:
            self.header = None
        self.timeout = 3
        self.fields = "title,authors,abstract,citationCount,referenceCount,externalIds,year"
        self.limit = 10

    def _request(self, url):
        try:
            response = requests.get(url, headers=self.header, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                print("Failed to fetch data")
                return None
        except Exception as e:
            print("Failed to fetch data:", e)
            return None

    def fetch_paper(self, paper_id):
        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields={self.fields}&limit={self.limit}"
        return self._request(url)
    
    def fetch_citations(self, paper_id):
        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations?fields={self.fields}&limit={self.limit}"
        return self._request(url)
        
    def fetch_references(self, paper_id):
        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references?fields={self.fields}&limit={self.limit}"
        return self._request(url)
