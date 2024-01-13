import requests

class SemanticScholarAPI:

    def __init__(self):
        pass

    def fetch_data_from_api(self, paper_id):
        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations?fields=title,citationCount,externalIds,abstract"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to fetch data")
            return None
