# different form user.py from user service
from flask_login import UserMixin
import requests
import json
from pymongo import MongoClient
from bson import ObjectId

# user_url = 'https://cs518userserviceronang.azurewebsites.net/api/user/' #DEPLOYED
# func_key = 'REDACTED' #DEPLOYED

func_key = None #LOCAL
user_url = "http://localhost:7071/api/user/" #LOCAL

# all this from here...
# client = MongoClient("mongodb://localhost:27017")  # MongoDB connection string finns
client = MongoClient("mongodb+srv://rdg1032:rdg1032@cluster0.ft2wh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # MongoDB connection string


db = client['mydatabase']  # Choose your database (replace 'your_database_name' with your actual DB name)
users_collection = db['mycollection']  # Access the 'users' collection in your database
# ... to here should not need to be in this file, database stuff should not happen in here, ut in other user.py I think?

class User(UserMixin):

    def __init__(self, user_id, username, password, friends=None):  # , admin=False):
        self.id = user_id
        self.username = username
        self.password = password
        self.friends = friends if friends is not None else [] # new
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
        friends = u.get('friends', [])
        # admin = u.get('admin')
        # the admin stuff is bonus
        user = User(user_id, un, pw, friends)  # , admin)
        return user

    def authenticate(username, password):
        ## TODO: user-service GET user by username and password
        res = requests.get(user_url,
                           params={"username": username, "password": password, "code": func_key})

        print(res.status_code)
        if res.status_code != 200: # something went wrong (200 is what it should send if success)s
            return
        # TODO: construct user, same as in 'get'
        u = json.loads(res.text)
        user_id = u.get('_id').get('$oid')
        pw = u.get('password')
        un = u.get('username')
        friends = u.get('friends', [])
        # admin = u.get('admin')
        # the admin stuff is bonus
        user = User(user_id, un, pw, friends)  # , admin)
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
                friends = user_data.get('friends', [])
                user = User(user_id, username, password, friends)

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
    #
    # def add_friend(self, friend_user_id):
    #     """
    #     Adds a friend to the user's friends list.
    #
    #     Args:
    #         friend_user_id (str): The user ID of the friend to add.
    #
    #     Returns:
    #         bool: True if the friend was added successfully, False otherwise.
    #     """
    #     # Prevent adding oneself as a friend
    #     if friend_user_id == self.id:
    #         print("You cannot add yourself as a friend.")
    #         return False
    #
    #     # Prevent adding the same friend more than once
    #     if friend_user_id in self.friends:
    #         print(f"{friend_user_id} is already your friend.")
    #         return False  # Already friends
    #
    #     try:
    #         # Use $push to safely add the friend to the friends array
    #
    #         result = users_collection.update_one(
    #             {"_id": ObjectId(self.id)},  # Match the user by their unique ID
    #             {"$push": {"friends": friend_user_id}},  # Add friend to the array
    #             upsert=False  # Don't insert a new document, just update
    #         )
    #
    #         # Debug the result
    #         print(
    #             f"Matched: {result.matched_count}, Modified: {result.modified_count}, Upserted ID: {result.upserted_id}")
    #
    #         # Check if the update was successful
    #         if result.matched_count > 0 and result.modified_count > 0:
    #             print(f"User {friend_user_id} added as a friend.")
    #             return True
    #         elif result.matched_count == 0:
    #             print(f"User {self.id} not found in the database.")
    #             return False
    #         else:
    #             print("No changes made to the friends list.")
    #             return False
    #     except Exception as e:
    #         print(f"Error adding friend: {str(e)}")
    #         return False
    #
    # def remove_friend(self, friend_user_id):
    #     """
    #     Removes a friend from the user's friends list.
    #
    #     Args:
    #         friend_user_id (str): The user ID of the friend to remove.
    #
    #     Returns:
    #         bool: True if the friend was removed successfully, False otherwise.
    #     """
    #     if friend_user_id not in self.friends:
    #         print("This user is not in your friends list.")
    #         return False  # Not friends, nothing to remove
    #
    #     # Remove the friend and update the MongoDB document
    #     self.friends.remove(friend_user_id)
    #     friend_user = users_collection.find_one({"_id": ObjectId(friend_user_id)})
    #     friend_name = friend_user.get("name", "Unknown User")
    #     try:
    #         result = users_collection.update_one(
    #             {"_id": ObjectId(self.id)},
    #             {"$set": {"friends": self.friends}}
    #         )
    #         if result.modified_count > 0:
    #             print(f"User {friend_name} removed from friends list.")
    #             return True
    #         else:
    #             print("Failed to update friends list.")
    #             return False
    #     except Exception as e:
    #         print(f"Error removing friend: {str(e)}")
    #         return False