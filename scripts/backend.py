from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from dotenv import load_dotenv

from paperwalk.api import SemanticScholarAPI
from paperwalk.common.type import Paper, Relation
from paperwalk.database import Neo4jConnection, PaperDatabaseManager
from graphdatascience import GraphDataScience

load_dotenv()

app = Flask(__name__)
CORS(app)

conn = Neo4jConnection(
    uri=os.getenv("NEO4J_URI"),
    user=os.getenv("NEO4J_USER"),
    pwd=os.getenv("NEO4J_PWD"),
)

# gds = GraphDataScience(
#         os.getenv("NEO4J_URI"),
#         auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PWD")),
#         database="neo4j",
#     )

paper_db = PaperDatabaseManager(conn)

semantic_scholar_api = SemanticScholarAPI(api_key=os.getenv("SEMANTIC_SCHOLAR_API_KEY"))


@app.route("/papers/<paper_id>", methods=["GET"])
def get_paper(paper_id):
    """curl -X GET "http://localhost:5000/papers/649def34f8be52c8b66281af98ae884c09aef38b" -H "accept: application/json" """
    paper_data = semantic_scholar_api.fetch_paper(paper_id)
    return json.dumps(paper_data)


@app.route("/papers/<paper_id>/citations", methods=["GET"])
def get_citations(paper_id):
    citation_data = semantic_scholar_api.fetch_citations(paper_id)
    return json.dumps(citation_data)


@app.route("/papers/<paper_id>/references", methods=["GET"])
def get_references(paper_id):
    reference_data = semantic_scholar_api.fetch_references(paper_id)
    return json.dumps(reference_data)


@app.route("/papers/expand/<paper_id>", methods=["GET"])
def expand_paper(paper_id):
    citation_data = semantic_scholar_api.fetch_citations(paper_id)
    for citation in citation_data:
        paper_db.insert_citations_or_references_bulk(
            paper_id, citation, Relation.CITES
        )
    reference_data = semantic_scholar_api.fetch_references(paper_id)
    for reference in reference_data:
        paper_db.insert_citations_or_references_bulk(
            paper_id, reference, Relation.REFERENCES
        )
    return {"status": "success"}


if __name__ == "__main__":
    app.run(debug=True, port=5007)
