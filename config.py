from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId


client = MongoClient('localhost:27017')
db_name = 'DIGIDOONI'
db = client[db_name]
fs = GridFS(client[db_name + '_FS'])

models = db['MODELS']
models.drop_indexes()
models.create_index([("title.en", 1)])
models.create_index([("title.fa", 1)])
models.create_index([("title.compact", 1)])
models.create_index([("$**", "text")], weights={"$**": 1, "title": 3})
model = {
    'title': '',
    'price': 0,
}

products = db['PRODUCTS']
products.drop_indexes()
# products.create_index([("$**", "text")], weights={"$**": 1, "title": 3})
products.create_index([("model", 1)])
products.create_index([("_author", 1)])
pr = products

users = db['USERS']
users.drop_indexes()
users.create_index([('id', 1)])

keywords = db['KEYWORDS']
keywords.drop_indexes()
keywords.create_index([("word", 1)])
keyword = {
    'word': '',
    'count': 0,
}