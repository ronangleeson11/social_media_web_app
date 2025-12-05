import requests

from user import user
import azure.functions as func
import datetime
import json
import logging
from bson import json_util

app = func.FunctionApp()

user.connect("mongodb+srv://rdg1032:rdg1032@cluster0.ft2wh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Create user
@app.route(route="user", methods=['POST'], auth_level=func.AuthLevel.FUNCTION)
def create_user(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('creating user.')
    logging.warning(req.get_json())

    req_body = req.get_json()
    username = req_body.get('username')
    password = req_body.get('password')

    logging.warning(username + " " + password)

    uid = user.create_user(username, password)
    logging.warning(uid)

    return func.HttpResponse(str(uid))


# Read user
@app.route(route="user/{_id?}", methods=['GET'], auth_level=func.AuthLevel.FUNCTION)
def read_user(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('reading user.')

    # 1. get _id from route params
    # 2. call user.read_user
    # 3. use json_util.dumps to convert the user to a JSON str
    # 4. return the response
    id = req.route_params.get('_id')
    print(id)
    username = req.params.get('username')
    password = req.params.get('password')

    if id:
        r = user.read_user(id)
        if r is None:
            r = json_util.dumps(r)
            return func.HttpResponse(r, status_code=404)
        else:
            r = json_util.dumps(r)
            return func.HttpResponse(r, status_code=200)
    elif username and password:
        us = user.read_users({'username': username,
                              'password': password})
        us = list(us)
        if us:
            singleuser = us[0]
            return func.HttpResponse(json_util.dumps(singleuser))
        else:
            return func.HttpResponse("user not found", status_code=404)
    else:
        return func.HttpResponse(json_util.dumps(user.read_users({})))

    # if id is None:
    #     return func.HttpResponse(json_util.dumps(user.read_users({})))
    # r = user.read_user(id);
    # if r is None:
    #     r = json_util.dumps(r);
    #     return func.HttpResponse(r, status_code=404);
    # else:
    #     r = json_util.dumps(r);
    #     return func.HttpResponse(r, status_code=200);
    # NEED TO ADD IF ELSE TO SEE IF _ID WAS PROVIDED, IF IS PROVIDED, SHOW ONE USER, ELSE SHOW ALL


# Update user
@app.route(route="user/{_id?}", methods=['PUT'], auth_level=func.AuthLevel.FUNCTION)
def update_user(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('updating user.')
    id = req.route_params.get('_id')
    update = req.get_json()
    logging.warning(update)
    u = user.update_user(id, update)
    return func.HttpResponse(str(u), status_code=200)


# Delete user
@app.route(route="user/{_id?}", methods=['DELETE'], auth_level=func.AuthLevel.FUNCTION)
def delete_user(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('deleting user.')
    id = req.route_params.get('_id')
    d = user.delete_user(id)
    return func.HttpResponse(str(d), status_code=200)

# Upload post
@app.route(route="makepost/{_id?}", methods=['POST'], auth_level=func.AuthLevel.FUNCTION)
def upload_post(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('uploading post.')
    id = req.route_params.get('_id')
    req_body = req.get_json()
    txt = req_body.get('post_text')
    ret = user.upload_post(txt, id)
    return func.HttpResponse(str(ret), status_code=200)

# Read posts
@app.route(route="makepost/{_id?}", methods=['GET'], auth_level=func.AuthLevel.FUNCTION)
def read_posts(req: func.HttpRequest) -> func.HttpResponse:
    id = req.route_params.get('_id')
    print("id is:")
    print(id)

    if id:
        r = user.read_post(id)
        if r is None:
            r = json_util.dumps(r)
            return func.HttpResponse(r, status_code=404)
        else:
            r = json_util.dumps(r)
            return func.HttpResponse(r, status_code=200)
    else:
        return func.HttpResponse(json_util.dumps(user.read_posts({})))

    # if id is None:
    #     return func.HttpResponse(json_util.dumps(user.read_users({})))
    # r = user.read_user(id);
    # if r is None:
    #     r = json_util.dumps(r);
    #     return func.HttpResponse(r, status_code=404);
    # else:
    #     r = json_util.dumps(r);
    #     return func.HttpResponse(r, status_code=200);
    # NEED TO ADD IF ELSE TO SEE IF _ID WAS PROVIDED, IF IS PROV

# Read comments
@app.route(route="comment/{_id?}", methods=['GET'], auth_level=func.AuthLevel.FUNCTION)
def read_comments(req: func.HttpRequest) -> func.HttpResponse:
    id = req.route_params.get('_id')
    return func.HttpResponse(json_util.dumps(user.read_comments(id)))


@app.route(route="like/{post_id?}", methods=['POST'], auth_level=func.AuthLevel.FUNCTION)
def like_post(req: func.HttpRequest) -> func.HttpResponse:
    print("IN FUNCTION APP LIKE_POST")
    req_body = req.get_json()
    user_id = req_body.get('user_id')
    print(req.route_params.get('post_id'))
    print(req.route_params.get('post_id')[10:-2])
    post = user.read_post(req.route_params.get('post_id')[10:-2])
    if user_id not in post['likes']:
        print("liked")
        post['likes'].append(user_id)
    else:
        print("unliked")
        post['likes'].remove(user_id)
    print(post['likes'])
    ret = user.update_likes(req.route_params.get('post_id')[10:-2], post['likes'])
    return func.HttpResponse(status_code=200)

@app.route(route="delete/{post_id?}", methods=['DELETE'], auth_level=func.AuthLevel.FUNCTION)
def delete_post(req: func.HttpRequest) -> func.HttpResponse:
    print("IN FUNCTION APP DELETE_POST")
    ret = user.delete_post(req.route_params.get('post_id')[10:-2])
    return func.HttpResponse(status_code=200)

@app.route(route="comment/delete/{post_id?}/{comment_txt?}", methods=['DELETE'], auth_level=func.AuthLevel.FUNCTION)
def delete_comment(req: func.HttpRequest) -> func.HttpResponse:
    print("IN FUNCTION APP DELETE_COMMENT")
    ret = user.delete_comment(req.route_params.get('post_id'), req.route_params.get('comment_txt'))
    return func.HttpResponse(status_code=200)


@app.route(route="makecomment/{post_id?}", methods=['POST'], auth_level=func.AuthLevel.FUNCTION)
def make_comment(req: func.HttpRequest) -> func.HttpResponse:
    print("IN FUNCTION APP MAKE_COMMENT")
    req_body = req.get_json()
    user_id = req_body.get('user_id')
    txt = req_body.get('text')
    ret = user.make_comment(req.route_params.get('post_id'), user_id, txt)
    return func.HttpResponse(status_code=200)


@app.route(route="comment/like/{post_id?}/{comment_txt?}", methods=['POST'], auth_level=func.AuthLevel.FUNCTION)
def like_comment(req: func.HttpRequest) -> func.HttpResponse:
    print("IN FUNCTION APP LIKE_COMMENT")
    req_body = req.get_json()
    user_id = req_body.get('user_id')
    ret = user.like_comment(req.route_params.get('post_id'), req.route_params.get('comment_txt'), user_id)
    return func.HttpResponse(status_code=200)

@app.route(route="user/friend/{user_id?}/{friend_id?}", methods=['POST'], auth_level=func.AuthLevel.FUNCTION)
def add_friend(req: func.HttpRequest) -> func.HttpResponse:
   print("IN FUNCTION_APP ADD_FRIEND")
   user_id = req.route_params.get('user_id')
   friend_id = req.route_params.get('friend_id')
   ret = user.add_friend(user_id, friend_id)
   return func.HttpResponse(status_code=200)


@app.route(route="user/unfriend/{user_id?}/{friend_id?}", methods=['DELETE'], auth_level=func.AuthLevel.FUNCTION)
def remove_friend(req: func.HttpRequest) -> func.HttpResponse:
   print("IN FUNCTION_APP REMOVE_FRIEND")
   user_id = req.route_params.get('user_id')
   friend_id = req.route_params.get('friend_id')
   ret = user.remove_friend(user_id, friend_id)
   return func.HttpResponse(status_code=200)

