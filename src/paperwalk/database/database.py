from neo4j import GraphDatabase
from paperwalk.api import SemanticScholarAPI
import requests
from dotenv import load_dotenv
import os

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
        if self.__driver is not None:
            self.__driver.close()

    def clean(self):
        session = None
        try:
            session = self.__driver.session()
            session.run("MATCH (n) DETACH DELETE n")
        except Exception as e:
            print("Failed to clean the database:", e)
        finally:
            if session is not None:
                session.close()
        
    def query(self, query, parameters=None, db=None):
        session = None
        response = None
        try: 
            session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally: 
            if session is not None:
                session.close()
        return response

def insert_paper_data(conn, paper_id, paper_data):
    for citing_paper in paper_data['data']:
        query = '''
        MERGE (p1:Paper {paperId: $paperId})
        MERGE (p2:Paper {paperId: $citingPaperId})
        ON CREATE SET p2.title = $title, p2.abstract = $abstract, p2.citationCount = $citationCount
        MERGE (p2)-[:CITES]->(p1)
        '''
        parameters = {
            'paperId': paper_id,
            'citingPaperId': citing_paper['citingPaper']['paperId'],
            'title': citing_paper['citingPaper']['title'],
            'abstract': citing_paper['citingPaper']['abstract'],
            'citationCount': int(citing_paper['citingPaper']['citationCount']) if citing_paper['citingPaper']['citationCount'] else 0
        }
        conn.query(query, parameters)


if __name__ == "__main__":
    load_dotenv()
    conn = Neo4jConnection(uri=os.getenv("NEO4J_URI"), user=os.getenv("NEO4J_USER"), pwd=os.getenv("NEO4J_PWD"))
    conn.clean()

    semantic_scholar_api = SemanticScholarAPI()

    # Replace with the actual paper ID
    paper_id = "649def34f8be52c8b66281af98ae884c09aef38b"
    paper_data = semantic_scholar_api.fetch_data_from_api(paper_id)

    if paper_data:
        insert_paper_data(conn, paper_id, paper_data)

    # query
    query = '''
    MATCH (p:Paper)
    RETURN p.title, p.abstract, p.citationCount, p.citingPaperId
    '''
    result = conn.query(query)
    for record in result:
        print(record)

    conn.close()
