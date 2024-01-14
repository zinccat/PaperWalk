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
    conn.query(query, parameters)

def insert_citation_data(conn, paper_id, citation_data):
    for citing_paper in citation_data['data']:
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
        parameters = {
            'paperId': paper_id,
            'citingPaperId': citing_paper['citingPaper']['paperId'],
            'title': citing_paper['citingPaper']['title'],
            'firstAuthor': citing_paper['citingPaper']['authors'][0]['name'] if len(citing_paper['citingPaper']['authors']) > 0 else None,
            'firstAuthorId': citing_paper['citingPaper']['authors'][0]['authorId'] if len(citing_paper['citingPaper']['authors']) > 0 else None,
            'lastAuthor': citing_paper['citingPaper']['authors'][-1]['name'] if len(citing_paper['citingPaper']['authors']) > 0 else None,
            'lastAuthorId': citing_paper['citingPaper']['authors'][-1]['authorId'] if len(citing_paper['citingPaper']['authors']) > 0 else None,
            'abstract': citing_paper['citingPaper']['abstract'],
            'citationCount': int(citing_paper['citingPaper']['citationCount']) if citing_paper['citingPaper']['citationCount'] else 0,
            'referenceCount': int(citing_paper['citingPaper']['referenceCount']) if citing_paper['citingPaper']['referenceCount'] else 0,
            'ArXiv': citing_paper['citingPaper']['externalIds']['ArXiv'] if 'ArXiv' in citing_paper['citingPaper']['externalIds'] else None,
            'year': citing_paper['citingPaper']['year']
        }
        conn.query(query, parameters)

def insert_reference_data(conn, paper_id, reference_data):
    for reference_paper in reference_data['data']:
        query = '''
        MERGE (p1:Paper {paperId: $paperId})
        MERGE (p2:Paper {paperId: $referencePaperId})
        ON CREATE SET p2.title = $title, p2.firstAuthor = $firstAuthor, \
            p2.firstAuthorId = $firstAuthorId, p2.lastAuthor = $lastAuthor, \
            p2.lastAuthorId = $lastAuthorId, p2.abstract = $abstract, \
            p2.citationCount = $citationCount, p2.referenceCount = $referenceCount, \
            p2.ArXiv = $ArXiv, p2.year = $year
        MERGE (p1)-[:CITES]->(p2)
        '''
        print(reference_paper['citedPaper'])
        parameters = {
            'paperId': paper_id,
            'referencePaperId': reference_paper['citedPaper']['paperId'],
            'title': reference_paper['citedPaper']['title'],
            'firstAuthor': reference_paper['citedPaper']['authors'][0]['name'] if len(reference_paper['citedPaper']['authors']) > 0 else None,
            'firstAuthorId': reference_paper['citedPaper']['authors'][0]['authorId'] if len(reference_paper['citedPaper']['authors']) > 0 else None,
            'lastAuthor': reference_paper['citedPaper']['authors'][-1]['name'] if len(reference_paper['citedPaper']['authors']) > 0 else None,
            'lastAuthorId': reference_paper['citedPaper']['authors'][-1]['authorId'] if len(reference_paper['citedPaper']['authors']) > 0 else None,
            'abstract': reference_paper['citedPaper']['abstract'],
            'citationCount': int(reference_paper['citedPaper']['citationCount']) if reference_paper['citedPaper']['citationCount'] else 0,
            'referenceCount': int(reference_paper['citedPaper']['referenceCount']) if reference_paper['citedPaper']['referenceCount'] else 0,
            # externalIds is not always present
            'ArXiv': reference_paper['citedPaper']['externalIds']['ArXiv'] if reference_paper['citedPaper']['externalIds'] is not None and 'ArXiv' in reference_paper['citedPaper']['externalIds'] else None,
            'year': reference_paper['citedPaper']['year']
        }
        conn.query(query, parameters)

if __name__ == "__main__":
    load_dotenv()
    conn = Neo4jConnection(uri=os.getenv("NEO4J_URI"), user=os.getenv("NEO4J_USER"), pwd=os.getenv("NEO4J_PWD"))
    conn.clean()

    semantic_scholar_api = SemanticScholarAPI(api_key=os.getenv("SEMANTIC_SCHOLAR_API_KEY"))

    # Replace with the actual paper ID
    paper_id = "649def34f8be52c8b66281af98ae884c09aef38b"
    paper_data = semantic_scholar_api.fetch_paper(paper_id)
    if paper_data:
        insert_paper_data(conn, paper_id, paper_data)

    citation_data = semantic_scholar_api.fetch_citations(paper_id)
    if citation_data:
        insert_citation_data(conn, paper_id, citation_data)

    # for paper in citation_data['data'], search references
    for citing_paper in citation_data['data']:
        paper_id = citing_paper['citingPaper']['paperId']
        paper_data = semantic_scholar_api.fetch_paper(paper_id)
        if paper_data:
            insert_paper_data(conn, paper_id, paper_data)
        reference_data = semantic_scholar_api.fetch_references(paper_id)
        if reference_data:
            insert_reference_data(conn, paper_id, reference_data)

    # query
    query = '''
    MATCH (p:Paper)
    RETURN p.title, p.abstract, p.citationCount, p.citingPaperId
    '''
    result = conn.query(query)
    for record in result:
        print(record)

    conn.close()
