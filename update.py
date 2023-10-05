from pymongo import MongoClient

# Kết nối tới MongoDB
client = MongoClient('mongodb://10.254.59.57:27017/')

# Chọn database
db = client['pool_football']

# Chọn collection
collection = db['teams']


def remove_space(txt):
    return txt.replace(" ", "")


# Loop through each document in the collection
for document in collection.find():
    # Extract and modify the shortName
    modified_short_name = remove_space(document['shortName'])

    # Construct new image URL
    new_image_url = f'http://10.254.59.57:3000/images/{modified_short_name}.png'


    # Update the 'image' field in the database
    collection.update_one({'_id': document['_id']}, {'$set': {'image': new_image_url}})
