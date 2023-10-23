from pymongo import MongoClient
import bcrypt

client = MongoClient('mongodb://admin:secret@127.0.0.1:27017/')

db = client['task_board']
tasks_collection = db['tasks']

db = client['Users_DataBase']
user_collection = db['users']


def get_user_from_db(username, password):
    # Fetch the user from the database by username
    user = user_collection.find_one({"username": username})

    # If user exists and password matches
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return user
    else:
        return None


def get_users_collection():
    return user_collection


def get_tasks_collection():
    return tasks_collection


def insert_user(username, password, email):
    try:
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user_document = {
            'username': username,
            'password': hashed_pw.decode('utf-8'),
            'email': email
        }

        user_collection.insert_one(user_document)
        return user_document['_id']

    except Exception as e:
        print(f"An error occurred during user registration: {e}")
        return None
