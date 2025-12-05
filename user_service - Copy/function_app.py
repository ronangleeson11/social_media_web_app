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
    id = req.route_params.get('_id');
    print(id)
    username = req.params.get('username')
    password = req.params.get('password')

    if id:
        r = user.read_user(id);
        if r is None:
            r = json_util.dumps(r);
            return func.HttpResponse(r, status_code=404);
        else:
            r = json_util.dumps(r);
            return func.HttpResponse(r, status_code=200);
    elif username and password:
        us = user.read_users({'username': username,
                              'password': password})
        us = list(us)
        if us:
            singleuser = us[0]
            return func.HttpResponse(json_util.dumps(singleuser))
        else:
            return func.HttpResponse("user not found", status_code=404);
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
    id = req.route_params.get('_id');
    update = req.get_json();
    logging.warning(update)
    u = user.update_user(id, update);
    return func.HttpResponse(str(u), status_code=200);


# Delete user
@app.route(route="user/{_id?}", methods=['DELETE'], auth_level=func.AuthLevel.FUNCTION)
def delete_user(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('deleting user.')
    id = req.route_params.get('_id');
    d = user.delete_user(id);
    return func.HttpResponse(str(d), status_code=200)

# Upload post
@app.route(route="makepost/{_id?}", methods=['POST'], auth_level=func.AuthLevel.FUNCTION)
def upload_post(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('uploading post.')
    id = req.route_params.get('_id');
    req_body = req.get_json();
    txt = req_body.get('post_text')
    ret = user.upload_post(txt, id);
    return func.HttpResponse(str(ret), status_code=200)

# Upload post
@app.route(route="makepost/{_id?}", methods=['GET'], auth_level=func.AuthLevel.FUNCTION)
def read_posts(req: func.HttpRequest) -> func.HttpResponse:
    id = req.route_params.get('_id');
    print(id)

    if id:
        r = user.read_post(id);
        if r is None:
            r = json_util.dumps(r);
            return func.HttpResponse(r, status_code=404);
        else:
            r = json_util.dumps(r);
            return func.HttpResponse(r, status_code=200);
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