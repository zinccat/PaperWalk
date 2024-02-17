import os

from neo4j import GraphDatabase
from graphdatascience import GraphDataScience
from dotenv import load_dotenv
from paperwalk.api import SemanticScholarAPI
from paperwalk.common.type import Paper, Relation
from paperwalk.database import Neo4jConnection, PaperDatabaseManager

if __name__ == "__main__":
    load_dotenv()
    conn = Neo4jConnection(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        pwd=os.getenv("NEO4J_PWD"),
    )
    gds = GraphDataScience(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PWD")),
        database="neo4j",
    )
    paper_db = PaperDatabaseManager(conn, gds)
    paper_db.clean_database()

    semantic_scholar_api = SemanticScholarAPI(
        api_key=os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    )

    # Replace with the actual paper ID
    paper_id = "649def34f8be52c8b66281af98ae884c09aef38b"
    paper_data = semantic_scholar_api.fetch_paper(paper_id)

    if paper_data:
        paper_db.insert_paper(paper_id, paper_data)

    citation_data = semantic_scholar_api.fetch_citations(paper_id)
    for citation in citation_data:
        paper_db.insert_citations_or_references_bulk(paper_id, citation, Relation.CITES)
        # for paper in citation_data['data'],
        for citing_paper in citation["data"]:
            paper_id = citing_paper["citingPaper"]["paperId"]
            paper_data = semantic_scholar_api.fetch_paper(paper_id)
            if paper_data:
                paper_db.insert_paper(paper_id, paper_data)
            reference_data = semantic_scholar_api.fetch_references(paper_id)
            for reference in reference_data:
                paper_db.insert_citations_or_references_bulk(
                    paper_id, reference, Relation.REFERENCES
                )

    paper_db.run_pagerank()

    # query
    query = """
    MATCH (p:Paper)
    RETURN p.title, p.abstract, p.citationCount, p.citingPaperId
    """
    result = conn.execute_query(query, protected=False)
    for record in result:
        print(record)

    conn.close()
