from pymongo import MongoClient

# Kết nối tới MongoDB
client = MongoClient('mongodb://10.254.59.57:27017/')

# Chọn database
db = client['pool_football']

lst_collection = ['teams', 'tournaments', 'uniquetournaments']

for i in lst_collection:
    # Chọn collection
    collection = db[f'{i}']

    # Loop through each document in the collection
    for document in collection.find():
        a = document['image'].replace('http://10.254.59.57/api/bigpool/images/', '/bpimages/')

        collection.update_one({'_id': document['_id']}, {'$set': {'image': a}})
