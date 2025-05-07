from flask_pymongo import PyMongo
from elasticsearch import Elasticsearch

# Initialize extensions
mongo = PyMongo()

class ElasticsearchExt:
    def __init__(self):
        self.es = None
        
    def init_app(self, app):
        self.es = Elasticsearch(app.config['ELASTICSEARCH_URL'])

es = ElasticsearchExt()