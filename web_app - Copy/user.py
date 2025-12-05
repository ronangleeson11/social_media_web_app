# different form user.py from user service
from flask_login import UserMixin
import requests
import json
from pymongo import MongoClient
from bson import ObjectId
user_url = 'https://cs518userserviceronang.azurewebsites.net/api/user/' #DEPLOYED
# user_url = "http://localhost:7071/api/user/" #LOCAL
func_key = 't8J6d5Q6_j_DhBCwq42BktPCNljBEkEPCaAYP3STDz2DAzFuLOlooA==' #DEPLOYED
# func_key = None #LOCAL

# client = MongoClient("mongodb://localhost:27017")  # MongoDB connection string finns
client = MongoClient("mongodb+srv://rdg1032:rdg1032@cluster0.ft2wh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # MongoDB connection string



db = client['mydatabase']  # Choose your database (replace 'your_database_name' with your actual DB name)
users_collection = db['mycollection']  # Access the 'users' collection in your database


class User(UserMixin):

    def __init__(self, user_id, username, password):  # , admin=False):
        self.id = user_id
        self.username = username
        self.password = password
        # self.admin = admin

    def get(user_id):
        ## TODO: Make a request to your user-service to GET user by id
        res = requests.get(user_url+user_id,
                           params={"code": func_key})# user url? in tsead of user id?

        print("TEXT: ", res.text, " ", user_id)
        u = json.loads(res.text)
        print(u)
        user_id = u.get('_id').get('$oid')
        pw = u.get('password')
        un = u.get('username')
        # admin = u.get('admin')
        # the admin stuff is bonus
        user = User(user_id, un, pw)  # , admin)
        return user

    def authenticate(username, password):
        ## TODO: user-service GET user by username and password
        res = requests.get(user_url,
                           params={"username": username, "password": password, "code": func_key})

        if res.status_code != 200: # something went wrong (200 is what it should send if success)s
            return

        # TODO: construct user, same as in 'get'
        u = json.loads(res.text)
        user_id = u.get('_id').get('$oid')
        pw = u.get('password')
        un = u.get('username')
        # admin = u.get('admin')
        # the admin stuff is bonus
        user = User(user_id, un, pw)  # , admin)
        return user

    def update_bio(self, user_id, new_bio):
        """
        Update the bio for this user in MongoDB.

        Args:
            new_bio (str): The new bio text to update for the user.

        Returns:
            bool: True if the bio was updated successfully, False otherwise.
        """

        try:
            res = requests.get(f"{user_url}/{user_id}", params={"code": func_key})
            res.raise_for_status()

            if res.status_code == 200:
                user_data = res.json()

                # Step 2: Use the user_data to check if the user exists
                user_id = user_data.get('_id', {}).get('$oid')
                username = user_data.get('username')
                password = user_data.get('password')
                user = User(user_id, username, password)

                # Step 3: Update the bio field for this user
                # Ensure the user_id is valid and convert it to ObjectId
                if ObjectId.is_valid(user.id):
                    result = users_collection.update_one(
                        {"_id": ObjectId(user.id)},  # Use ObjectId for MongoDB ID lookup
                        {"$set": {"bio": new_bio}}  # Set the new bio value
                    )

                    if result.modified_count > 0:
                        print(f"Bio updated for user {user.id}")
                        return True  # Successfully updated the bio
                    else:
                        print(f"Failed to update bio for user {user.id}")
                        return False  # Failing here
                else:
                    print(f"Invalid user ID: {user.id}")
                    return False

            else:
                print(f"User not found with ID {user_id}")
                return False

        except requests.RequestException as e:
            print(f"Error fetching user: {str(e)}")
            return False



