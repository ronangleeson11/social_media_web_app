from bson import ObjectId
import pymongo

# import user_service.user.user

mycol = None
ourposts = None

### Initialization and reset

def connect(conn_str: str):
    """connect to the client and initialize mycol.  returns none."""
    global mycol
    global ourposts
    myclient = pymongo.MongoClient(conn_str)
    mydb = myclient["mydatabase"]
    mycol = mydb["mycollection"]
    ourposts = mydb["ourposts"]
    return None

def reset():
    """reset the collection.  returns none."""
    global mycol;
    mycol.drop()
    return None

### CRUD operations

def create_user(username: str, password: str) -> str:
    """returns id of new user"""
    global mycol
    user_data = {
        "username":username,
        "password":password,
        "addresses":[],
        "posts": []
    }
    x = mycol.insert_one(user_data)
    return x.inserted_id

def read_user(id: str) -> dict:
    """returns user document"""
    global mycol
    return mycol.find_one({"_id":ObjectId(id)})

def read_post(id: str) -> dict:
    """returns user document"""
    global ourposts
    return ourposts.find_one({"_id":ObjectId(id)})

def read_users(query: dict) -> list:
    """returns a cursor of user documents matching the query"""
    global mycol
    users = []
    for x in mycol.find(query):
        users.append(x)
    return users

def read_posts(query: dict) -> list:
    """returns a cursor of user documents matching the query"""
    global ourposts
    posts = []
    for x in ourposts.find(query):
        posts.append(x)
    return posts

def update_user_pass(username, newpass):
    global mycol
    """returns updateresult."""
    myquery = {"username":username}
    myquery_new = {"password":newpass}
    x = mycol.update_one(myquery, {"$set":myquery_new})
    return x

def delete_user(id:str):
    """returns deleteresult"""
    global mycol;
    x = mycol.delete_one({"_id":ObjectId(id)}).deleted_count
    return x

############## User address

def add_user_address(id, addr):
    global mycol
    """params: id is user id, addr is a dict.  returns: updateresult"""
    myquery = {"_id":id}
    addresses_new = mycol.find_one(myquery).get("addresses")
    addresses_new.append(addr)
    myquery_new = {"addresses":addresses_new}
    x = mycol.update_one(myquery, {"$set": myquery_new})
    return x

def get_user_addresses(id):
    global mycol
    """params: id is user id.  returns: list of addresses for given user"""
    myquery = {"_id":id}
    addresses = mycol.find_one(myquery).get("addresses")
    return addresses

def update_user(id:str, update):
    """returns modified_count."""
    global mycol
    oid = ObjectId(id)
    result = mycol.update_one({'_id':oid},{'$set':update})
    return result.modified_count


def upload_post_user(txt, id):
    global mycol
    oid = ObjectId(id)
    myquery = {"_id":oid}
    result = mycol.update_one(myquery, {'$addToSet':{'posts':txt}})

def upload_post(txt, id):
    global ourposts
    oid = ObjectId(id)
    post_data = {
        "uid": id,
        "name": read_user(id).get("username"),
        "txt": txt
    }
    res = ourposts.insert_one(post_data)
    upload_post_user(txt, id)
    return str(res.inserted_id)
