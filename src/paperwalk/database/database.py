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
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__password))
            self.__driver.verify_connectivity()
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver:
            self.__driver.close()

    def execute_query(self, query, parameters=None, db=None):
        # with self.__driver.session(database=db) as session:
        #     return session.run(query, parameters)
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
        # Create a graph projection
        # create_projection_query = """
        # CALL gds.graph.project(
        #     'papersGraph6',
        #     'Paper',
        #     'CITES'
        # )
        # """
        # result = self.conn.execute_query(create_projection_query)
        # print(result.result())
        # exit()
        G_papers, projection = self.gds.graph.project(
            graph_name="papersGraph",
            relationship_spec="CITES",
            node_spec="Paper",
        )
        # print(G_papers)
        # print(projection)
        # print(G_papers.node_count())

        # Run PageRank
        # results = self.gds.pageRank.stream(self.gds.graph.get("papersGraph"))
        # print(results)

        results = self.gds.pageRank.write(
            G=G_papers, #self.gds.graph.get("papersGraph"),
            maxIterations=20,
            dampingFactor=0.85,
            writeProperty="pagerank",
        )

        results = self.gds.articleRank.write(
            G=G_papers, 
            writeProperty="articlerank",
        )
        
        # pagerank_query = """
        # CALL gds.pageRank.write('papersGraph', {
        #     maxIterations: 20,
        #     dampingFactor: 0.85,
        #     writeProperty: 'pagerank'
        # })
        # """
        # self.conn.execute_query(pagerank_query)

        # # Drop the graph projection if needed
        # drop_projection_query = "CALL gds.graph.drop('papersGraph')"
        # self.conn.execute_query(drop_projection_query)

        # self.logger.info("PageRank algorithm executed successfully.")

        # Query the top 10 papers
        # query = """
        # MATCH (p:Paper)
        # RETURN p.title, p.pagerank
        # ORDER BY p.pagerank DESC
        # LIMIT 10
        # """
        # result = self.conn.execute_query(query)
        # for record in result:
        #     print(record)
    
    def insert_paper(self, paper_id, paper_data):
        query = '''
        MERGE (p:Paper {paperId: $paperId})
        ON CREATE SET p.title = $title, p.firstAuthor = $firstAuthor, \
            p.firstAuthorId = $firstAuthorId, p.lastAuthor = $lastAuthor, \
            p.lastAuthorId = $lastAuthorId, p.abstract = $abstract, \
            p.citationCount = $citationCount, p.referenceCount = $referenceCount, \
            p.ArXiv = $ArXiv, p.year = $year
        '''
        parameters = {
            'paperId': paper_id,
            'title': paper_data['title'],
            'firstAuthor': paper_data['authors'][0]['name'] if len(paper_data['authors']) > 0 else None,
            'firstAuthorId': paper_data['authors'][0]['authorId'] if len(paper_data['authors']) > 0 else None,
            'lastAuthor': paper_data['authors'][-1]['name'] if len(paper_data['authors']) > 0 else None,
            'lastAuthorId': paper_data['authors'][-1]['authorId'] if len(paper_data['authors']) > 0 else None,
            'abstract': paper_data['abstract'],
            'citationCount': int(paper_data['citationCount']) if paper_data['citationCount'] else 0,
            'referenceCount': int(paper_data['referenceCount']) if paper_data['referenceCount'] else 0,
            'ArXiv': paper_data['externalIds']['ArXiv'] if 'ArXiv' in paper_data['externalIds'] else None,
            'year': paper_data['year']
        }
        try:
            self.conn.execute_query(query, parameters)
            self.logger.info(f"Inserted paper {paper_id}.")
        except Exception as e:
            self.logger.error(f"Error inserting paper {paper_id}: {e}")

    def insert_citation_or_reference(self, paper_id, paper_data, relation: Relation):
        if relation == Relation.CITES:
            query = '''
            MERGE (p1:Paper {paperId: $paperId})
            MERGE (p2:Paper {paperId: $citingPaperId})
            ON CREATE SET p2.title = $title, p2.firstAuthor = $firstAuthor, \
                p2.firstAuthorId = $firstAuthorId, p2.lastAuthor = $lastAuthor, \
                p2.lastAuthorId = $lastAuthorId, p2.abstract = $abstract, \
                p2.citationCount = $citationCount, p2.referenceCount = $referenceCount, \
                p2.ArXiv = $ArXiv, p2.year = $year
            MERGE (p2)-[:CITES]->(p1)
            '''
            key = 'citingPaper'
        elif relation == Relation.REFERENCES:
            # inverse of CITES
            query = '''
            MERGE (p1:Paper {paperId: $paperId})
            MERGE (p2:Paper {paperId: $citingPaperId})
            ON CREATE SET p2.title = $title, p2.firstAuthor = $firstAuthor, \
                p2.firstAuthorId = $firstAuthorId, p2.lastAuthor = $lastAuthor, \
                p2.lastAuthorId = $lastAuthorId, p2.abstract = $abstract, \
                p2.citationCount = $citationCount, p2.referenceCount = $referenceCount, \
                p2.ArXiv = $ArXiv, p2.year = $year
            MERGE (p1)-[:REFERENCES]->(p2)
            '''
            key = 'citedPaper'
        
        for relation_paper in paper_data['data']:
            parameters = {
                'paperId': paper_id,
                'citingPaperId': relation_paper[key]['paperId'],
                'title': relation_paper[key]['title'],
                'firstAuthor': relation_paper[key]['authors'][0]['name'] if len(relation_paper[key]['authors']) > 0 else None,
                'firstAuthorId': relation_paper[key]['authors'][0]['authorId'] if len(relation_paper[key]['authors']) > 0 else None,
                'lastAuthor': relation_paper[key]['authors'][-1]['name'] if len(relation_paper[key]['authors']) > 0 else None,
                'lastAuthorId': relation_paper[key]['authors'][-1]['authorId'] if len(relation_paper[key]['authors']) > 0 else None,
                'abstract': relation_paper[key]['abstract'],
                'citationCount': int(relation_paper[key]['citationCount']) if relation_paper[key]['citationCount'] else 0,
                'referenceCount': int(relation_paper[key]['referenceCount']) if relation_paper[key]['referenceCount'] else 0,
                # externalIds is not always present
                'ArXiv': relation_paper[key]['externalIds']['ArXiv'] if relation_paper[key]['externalIds'] is not None and 'ArXiv' in relation_paper[key]['externalIds'] else None,
                'year': relation_paper[key]['year']
            }
            try:
                self.conn.execute_query(query, parameters)
                self.logger.info(f"Inserted paper {relation_paper[key]['paperId']}.")
            except Exception as e:
                self.logger.error(f"Error inserting paper {relation_paper[key]['paperId']}: {e}")

if __name__ == "__main__":
    load_dotenv()
    conn = Neo4jConnection(uri=os.getenv("NEO4J_URI"), user=os.getenv("NEO4J_USER"), pwd=os.getenv("NEO4J_PWD"))
    gds = GraphDataScience(os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PWD")), database="neo4j")
    paper_db = PaperDatabaseManager(conn, gds)
    paper_db.clean_database()

    semantic_scholar_api = SemanticScholarAPI(api_key=os.getenv("SEMANTIC_SCHOLAR_API_KEY"))

    # Replace with the actual paper ID
    paper_id = "649def34f8be52c8b66281af98ae884c09aef38b"
    paper_data = semantic_scholar_api.fetch_paper(paper_id)
    if paper_data:
        paper_db.insert_paper(paper_id, paper_data)

    citation_data = semantic_scholar_api.fetch_citations(paper_id)
    if citation_data:
        paper_db.insert_citation_or_reference(paper_id, citation_data, Relation.CITES)

    # for paper in citation_data['data'], search references
    # for citing_paper in citation_data['data']:
    #     paper_id = citing_paper['citingPaper']['paperId']
    #     paper_data = semantic_scholar_api.fetch_paper(paper_id)
    #     if paper_data:
    #         paper_db.insert_paper(paper_id, paper_data)
    #     reference_data = semantic_scholar_api.fetch_references(paper_id)
    #     if reference_data:
    #         paper_db.insert_citation_or_reference(paper_id, reference_data, Relation.REFERENCES)

    paper_db.run_pagerank()

    # query
    # query = '''
    # MATCH (p:Paper)
    # RETURN p.title, p.abstract, p.citationCount, p.citingPaperId
    # '''
    # result = conn.execute_query(query)
    # for record in result:
    #     print(record)

    conn.close()
