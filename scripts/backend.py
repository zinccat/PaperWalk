import json
import os
from dotenv import load_dotenv
from typing import Union

from paperwalk.api import SemanticScholarAPI
from paperwalk.common.type import Paper, Relation
from paperwalk.database import Neo4jConnection, PaperDatabaseManager
from graphdatascience import GraphDataScience
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

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

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5007",
    "http://localhost:8082",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/papers/{paper_id}", response_model=Paper)
async def get_paper(paper_id: str):
    """Fetch paper data by ID."""
    paper_data = semantic_scholar_api.fetch_paper(paper_id)
    return paper_data

# insert paper
@app.post("/papers", response_model=dict)
async def insert_paper(paper_id: str):
    """Insert paper data into the database."""
    paper_data = await get_paper(paper_id)
    paper_db.insert_paper(paper_id, paper_data)
    return {"status": "success"}

@app.get("/papers/{paper_id}/citations", response_model=Union[dict, list])  # Adjust the response_model as needed
async def get_citations(paper_id: str):
    """Fetch citation data for a paper by ID."""
    citation_data = semantic_scholar_api.fetch_citations(paper_id)
    return citation_data

@app.get("/papers/{paper_id}/references", response_model=Union[dict, list])  # Adjust the response_model as needed
async def get_references(paper_id: str):
    """Fetch reference data for a paper by ID."""
    reference_data = semantic_scholar_api.fetch_references(paper_id)
    return reference_data

@app.get("/papers/expand/{paper_id}", response_model=dict)
async def expand_paper(paper_id: str):
    """Expand paper information by fetching and storing its citations and references."""
    citation_data = semantic_scholar_api.fetch_citations(paper_id)
    for citation in citation_data:
        paper_db.insert_citations_or_references_bulk(paper_id, citation, Relation.CITES)
    reference_data = semantic_scholar_api.fetch_references(paper_id)
    for reference in reference_data:
        paper_db.insert_citations_or_references_bulk(paper_id, reference, Relation.REFERENCES)
    return {"status": "success"}

@app.get("/search", response_model=Union[dict, list])  # Adjust the response_model as needed
async def search_papers(query: str):
    """Search papers."""
    search_results = semantic_scholar_api.search_papers(query)
    for results in search_results:
        res = results["data"]
        for paper in res:
            paper_db.insert_paper(paper["paperId"], paper)
    return search_results

@app.post("/clean", response_model=dict)
async def clean_database():
    """Clean the database."""
    paper_db.clean_database()
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5007)