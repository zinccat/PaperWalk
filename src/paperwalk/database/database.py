from neo4j import GraphDatabase
from graphdatascience import GraphDataScience
from paperwalk.api import SemanticScholarAPI
import requests
import logging
from dotenv import load_dotenv
import os
from paperwalk.common.type import Paper, Relation

logging.basicConfig(level=logging.INFO)


class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__password = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(
                self.__uri,
                auth=(self.__user, self.__password),
                encrypted=False,
                connection_timeout=5,
            )
            self.__driver.verify_connectivity()
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver:
            self.__driver.close()

    def execute_query(self, query, parameters=None, db=None, protected=True):
        if protected:
            with self.__driver.session(database=db) as session:
                return session.run(query, parameters)
        else:
            return self.__driver.session(database=db).run(query, parameters)


class PaperDatabaseManager:
    def __init__(self, neo4j_connection, gds: GraphDataScience = None):
        self.conn = neo4j_connection
        if gds:
            self.gds = gds
        self.logger = logging.getLogger(__name__)

    def clean_database(self):
        try:
            self.conn.execute_query("MATCH (n) DETACH DELETE n")
            self.gds.graph.drop(self.gds.graph.get("papersGraph"))
            # graphs = self.gds.graph.list()
            # for graph in graphs:
            #     self.gds.graph.drop(self.gds.graph.get(graph))
            self.logger.info("Database cleaned successfully.")
        except Exception as e:
            print("Failed to clean the database:", e)

    def run_pagerank(self):
        G_papers, projection = self.gds.graph.project(
            graph_name="papersGraph",
            relationship_spec="CITES",
            node_spec="Paper",
        )

        # Run PageRank
        # results = self.gds.pageRank.stream(self.gds.graph.get("papersGraph"))
        # print(results)

        results = self.gds.pageRank.write(
            G=G_papers,  # self.gds.graph.get("papersGraph"),
            maxIterations=20,
            dampingFactor=0.85,
            writeProperty="pagerank",
        )

        results = self.gds.articleRank.write(
            G=G_papers,
            writeProperty="articlerank",
        )

    def insert_paper(self, paper_id, paper_data):
        query = """
        MERGE (p:Paper {paperId: $paperId})
        ON CREATE SET p.title = $title, p.firstAuthor = $firstAuthor, \
            p.firstAuthorId = $firstAuthorId, p.lastAuthor = $lastAuthor, \
            p.lastAuthorId = $lastAuthorId, p.abstract = $abstract, \
            p.citationCount = $citationCount, p.referenceCount = $referenceCount, \
            p.ArXiv = $ArXiv, p.year = $year
        """
        authors = paper_data.get("authors", [])
        paper_param = {
            "paperId": paper_data["paperId"],
            "title": paper_data.get("title"),
            "firstAuthor": authors[0].get("name") if authors else None,
            "firstAuthorId": authors[0].get("authorId") if authors else None,
            "lastAuthor": authors[-1].get("name") if authors else None,
            "lastAuthorId": authors[-1].get("authorId") if authors else None,
            "abstract": paper_data.get("abstract"),
            "citationCount": int(paper_data.get("citationCount", 0)),
            "referenceCount": int(paper_data.get("referenceCount", 0)),
            "ArXiv": paper_data.get("externalIds", {}).get("ArXiv"),
            "year": paper_data.get("year"),
        }
        try:
            self.conn.execute_query(query, paper_param)
            self.logger.info(f"Inserted paper {paper_id}.")
        except Exception as e:
            self.logger.error(f"Error inserting paper {paper_id}: {e}")

    def insert_papers_bulk(self, papers_data):
        query = """
        UNWIND $papers as paper
        MERGE (p:Paper {paperId: paper.paperId})
        ON CREATE SET p.title = paper.title, p.firstAuthor = paper.firstAuthor, 
            p.firstAuthorId = paper.firstAuthorId, p.lastAuthor = paper.lastAuthor, 
            p.lastAuthorId = paper.lastAuthorId, p.abstract = paper.abstract, 
            p.citationCount = paper.citationCount, p.referenceCount = paper.referenceCount, 
            p.ArXiv = paper.ArXiv, p.year = paper.year
        """
        papers_parameters = []
        for paper_data in papers_data:
            authors = paper_data.get("authors", [])
            paper_param = {
                "paperId": paper_data["paperId"],
                "title": paper_data.get("title"),
                "firstAuthor": authors[0].get("name") if authors else None,
                "firstAuthorId": authors[0].get("authorId") if authors else None,
                "lastAuthor": authors[-1].get("name") if authors else None,
                "lastAuthorId": authors[-1].get("authorId") if authors else None,
                "abstract": paper_data.get("abstract"),
                "citationCount": int(paper_data.get("citationCount", 0)),
                "referenceCount": int(paper_data.get("referenceCount", 0)),
                "ArXiv": paper_data.get("externalIds", {}).get("ArXiv"),
                "year": paper_data.get("year"),
            }
            papers_parameters.append(paper_param)

        parameters = {"papers": papers_parameters}

        try:
            self.conn.execute_query(query, parameters)
            self.logger.info(f"Bulk inserted {len(papers_parameters)} papers.")
        except Exception as e:
            self.logger.error(f"Error in bulk insertion: {e}")

    def insert_citation_or_reference(self, paper_id, paper_data, relation: Relation):
        if relation == Relation.CITES:
            query = """
            MERGE (p1:Paper {paperId: $paperId})
            MERGE (p2:Paper {paperId: $citingPaperId})
            ON CREATE SET p2.title = $title, p2.firstAuthor = $firstAuthor, \
                p2.firstAuthorId = $firstAuthorId, p2.lastAuthor = $lastAuthor, \
                p2.lastAuthorId = $lastAuthorId, p2.abstract = $abstract, \
                p2.citationCount = $citationCount, p2.referenceCount = $referenceCount, \
                p2.ArXiv = $ArXiv, p2.year = $year
            MERGE (p2)-[:CITES]->(p1)
            """
            key = "citingPaper"
        elif relation == Relation.REFERENCES:
            query = """
            MERGE (p1:Paper {paperId: $paperId})
            MERGE (p2:Paper {paperId: $citingPaperId})
            ON CREATE SET p2.title = $title, p2.firstAuthor = $firstAuthor, \
                p2.firstAuthorId = $firstAuthorId, p2.lastAuthor = $lastAuthor, \
                p2.lastAuthorId = $lastAuthorId, p2.abstract = $abstract, \
                p2.citationCount = $citationCount, p2.referenceCount = $referenceCount, \
                p2.ArXiv = $ArXiv, p2.year = $year
            MERGE (p1)-[:CITES]->(p2)
            """
            key = "citedPaper"

        for relation_paper in paper_data["data"]:
            paper_info = relation_paper.get(key, {})
            authors = paper_info.get("authors", [])
            parameters = {
                "paperId": paper_id,
                "citingPaperId": paper_info.get("paperId"),
                "title": paper_info.get("title"),
                "firstAuthor": authors[0].get("name") if authors else None,
                "firstAuthorId": authors[0].get("authorId") if authors else None,
                "lastAuthor": authors[-1].get("name") if authors else None,
                "lastAuthorId": authors[-1].get("authorId") if authors else None,
                "abstract": paper_info.get("abstract"),
                "citationCount": int(paper_info.get("citationCount", 0)),
                "referenceCount": int(paper_info.get("referenceCount", 0)),
                "ArXiv": paper_info.get("externalIds", {}).get("ArXiv"),
                "year": paper_info.get("year"),
                }
            try:
                self.conn.execute_query(query, parameters)
                self.logger.info(f"Inserted paper {paper_info.get('paperId')}.")
            except Exception as e:
                self.logger.error(f"Error inserting paper {paper_info.get('paperId')}: {e}")

    def insert_citations_or_references_bulk(
        self, paper_id, paper_data, relation: Relation
    ):
        if relation == Relation.CITES:
            query = """
            UNWIND $papers as paper
            MERGE (p1:Paper {paperId: $paperId})
            MERGE (p2:Paper {paperId: paper.citingPaperId})
            ON CREATE SET p2.title = paper.title, p2.firstAuthor = paper.firstAuthor, 
                p2.firstAuthorId = paper.firstAuthorId, p2.lastAuthor = paper.lastAuthor, 
                p2.lastAuthorId = paper.lastAuthorId, p2.abstract = paper.abstract, 
                p2.citationCount = paper.citationCount, p2.referenceCount = paper.referenceCount, 
                p2.ArXiv = paper.ArXiv, p2.year = paper.year
            MERGE (p2)-[:CITES]->(p1)
            """
            key = "citingPaper"
        elif relation == Relation.REFERENCES:
            query = """
            UNWIND $papers as paper
            MERGE (p1:Paper {paperId: $paperId})
            MERGE (p2:Paper {paperId: paper.citingPaperId})
            ON CREATE SET p2.title = paper.title, p2.firstAuthor = paper.firstAuthor, 
                p2.firstAuthorId = paper.firstAuthorId, p2.lastAuthor = paper.lastAuthor, 
                p2.lastAuthorId = paper.lastAuthorId, p2.abstract = paper.abstract, 
                p2.citationCount = paper.citationCount, p2.referenceCount = paper.referenceCount, 
                p2.ArXiv = paper.ArXiv, p2.year = paper.year
            MERGE (p1)-[:CITES]->(p2)
            """
            key = "citedPaper"

        papers_parameters = []
        for relation_paper in paper_data["data"]:
            paper_info = relation_paper.get(key, {})
            authors = paper_info.get("authors", [])
            parameters = {
                "paperId": paper_id,
                "citingPaperId": paper_info.get("paperId"),
                "title": paper_info.get("title"),
                "firstAuthor": authors[0].get("name") if authors else None,
                "firstAuthorId": authors[0].get("authorId") if authors else None,
                "lastAuthor": authors[-1].get("name") if authors else None,
                "lastAuthorId": authors[-1].get("authorId") if authors else None,
                "abstract": paper_info.get("abstract"),
                "citationCount": int(paper_info.get("citationCount", 0)),
                "referenceCount": int(paper_info.get("referenceCount", 0)),
                "ArXiv": paper_info.get("externalIds", {}).get("ArXiv"),
                "year": paper_info.get("year"),
                }
            papers_parameters.append(parameters)

        parameters = {"papers": papers_parameters, "paperId": paper_id}

        try:
            self.conn.execute_query(query, parameters)
            self.logger.info(f"Bulk inserted {len(papers_parameters)} papers.")
        except Exception as e:
            self.logger.error(f"Error in bulk insertion: {e}")


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
