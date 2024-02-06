import flask
import flask_cors
import json
import os
from dotenv import load_dotenv

from paperwalk.api import SemanticScholarAPI
from paperwalk.common.type import Paper, Relation

load_dotenv()

app = flask.Flask(__name__)
flask_cors.CORS(app)

@app.route("/papers/<paper_id>", methods=["GET"])
def get_paper(paper_id):
    '''curl -X GET "http://localhost:5000/papers/649def34f8be52c8b66281af98ae884c09aef38b" -H "accept: application/json"
    '''
    semantic_scholar_api = SemanticScholarAPI(
        api_key=os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    )
    paper_data = semantic_scholar_api.fetch_paper(paper_id)
    return json.dumps(paper_data)

@app.route("/papers/<paper_id>/citations", methods=["GET"])
def get_citations(paper_id):
    semantic_scholar_api = SemanticScholarAPI(
        api_key=os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    )
    citation_data = semantic_scholar_api.fetch_citations(paper_id)
    return json.dumps(citation_data)

@app.route("/papers/<paper_id>/references", methods=["GET"])
def get_references(paper_id):
    semantic_scholar_api = SemanticScholarAPI(
        api_key=os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    )
    reference_data = semantic_scholar_api.fetch_references(paper_id)
    return json.dumps(reference_data)

if __name__ == "__main__":
    app.run(debug=True)