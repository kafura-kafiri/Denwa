from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId


client = MongoClient('localhost:27017')
db_name = 'DIGIDOONI'
db = client[db_name]
fs = GridFS(client[db_name + '_FS'])

models = db['MODELS']
models.drop_indexes()
models.create_index([("model", 1)])
model = {
    'model': '',
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