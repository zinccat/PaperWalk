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

    def fetch_paper(self, paper_id):
        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields=title,authors,abstract,citationCount,referenceCount,externalIds,year&limit=10"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to fetch data")
            return None

    def fetch_citations(self, paper_id):
        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations?fields=title,authors,abstract,citationCount,referenceCount,externalIds,year&limit=10"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to fetch data")
            return None
        
    def fetch_references(self, paper_id):
        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references?fields=title,authors,abstract,citationCount,referenceCount,externalIds,year&limit=10"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to fetch data")
            return None
