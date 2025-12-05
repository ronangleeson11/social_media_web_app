from flask import Flask
from flask import render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from user import User
from flask import session

import requests
import json
# import os

# from user import user_url, func_key
#
# user_url = 'https://cs518userserviceronang.azurewebsites.net/api' #DEPLOYED
# func_key = 't8J6d5Q6_j_DhBCwq42BktPCNljBEkEPCaAYP3STDz2DAzFuLOlooA==' #DEPLOYED
#
user_url = 'http://localhost:7071/api' #LOCAL
func_key = None #LOCAL

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' # Needed for flashing for some reason
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-default-secret-key')


@app.route('/')
# @app.route('/feed/<posts>') # Problem is with this endpoint (not loading when posts passed in)
def index(posts=""): # why not just readposts in index here and then return url with posts=posts?
    # THIS GET REQUEST DOES NOT WORK WHEN DEPLOYED
    res = requests.get(user_url + '/makepost/',
                       params={"code": func_key})
    print(res.status_code) # RES RETURNS 404 WHEN DEPLOYED, ONE OF TWO THINGS:
    # EITHER NOT CONNECTING TO THE RIGHT DATABASE (LIKELY CUS USER SIGN IN WASNT WORKING) OR ID IS NOT NONE FOR SOME REASON
    ps = json.loads(res.text)
    print(ps) # use this instead of posts maybe to avoid session
    if posts:
        return render_template("index.html", posts=ps)
    else: # maybe change later to readposts instead of all of the session stuff?
        # posts = session.get('posts', [])
        # iterate through posts and remove posts not by friends
        return render_template("index.html", posts=ps)


@app.route('/friendfeed')
def friend_feed():
    res = requests.get(user_url + '/makepost/',
                       params={"code": func_key})
    print(res.status_code)  # RES RETURNS 404 WHEN DEPLOYED, ONE OF TWO THINGS:
    # EITHER NOT CONNECTING TO THE RIGHT DATABASE (LIKELY CUS USER SIGN IN WASNT WORKING) OR ID IS NOT NONE FOR SOME REASON
    ps = json.loads(res.text)
    print(ps)  # use this instead of posts maybe to avoid session
    return render_template("friendfeed.html", posts=ps)


@app.route('/user/create',methods=['GET', 'POST'])
def user_create():
    if request.method=='GET':
        return render_template('user-create.html')
    # else get form data and create user
    un = request.form.get('username')
    pw = request.form.get('password')
    if not(un and pw):
        flash("username or password missing")
        return redirect(url_for('user_create'))
    res = requests.post(user_url+'/user/', json={
        'username': un,
        'password': pw},
        headers={'x-functions-key': func_key})
    flash(f"created user {res.text}")
    return redirect(url_for("index")) # need to return to index, login required for this


@app.route('/users/')
@app.route('/users/<user_id>', methods=['POST', 'GET']) # remove post?
@login_required
def user_view(user_id=None): # user_id = ""?
    # if user id is not provided, get al users
    # if id is specified, get just that user and display user detail page

    # if request.method == 'POST':
    #     flash("delete: user_id does not match")

    if user_id is None: # if not user_id?
        res = requests.get(user_url+'/user/',
                           params={"code": func_key})
        us = json.loads(res.text)

        for u in us:
            u['_id'] = u['_id']['$oid'] # comment this out?

        return render_template('user-listing.html', users=us)
    res = requests.get(user_url+'/user/' + user_id,
                       params={"code": func_key})
    u = json.loads(res.text)
    # Get posts then serve with posts = ps? Then display in for loop?
    res = requests.get(user_url + '/makepost/',
                       params={"code": func_key})
    print(res.status_code)  # RES RETURNS 404 WHEN DEPLOYED, ONE OF TWO THINGS:
    # EITHER NOT CONNECTING TO THE RIGHT DATABASE (LIKELY CUS USER SIGN IN WASNT WORKING) OR ID IS NOT NONE FOR SOME REASON
    ps = json.loads(res.text)
    return render_template('user-detail.html', user=u, posts=ps)

@app.route('/feed/')
@app.route('/feed/<post_id>', methods=['POST', 'GET']) # remove post?
@login_required
def post_view(post_id=""): # user_id = ""?
    if post_id is None: # if not user_id?
        res = requests.get(user_url+'/makepost/',
                           params={"code": func_key})
        ps = json.loads(res.text)

        for p in ps:
            p['_id'] = p['_id']['$oid'] # comment this out?

        return render_template('index.html', posts=ps)
    return redirect(url_for('index'))
    # res = requests.get(user_url+'/makepost/' + post_id,
    #                    params={"code": func_key})
    # p = json.loads(res.text)
    # return render_template('user-detail.html', user=u)


# @app.route('/user/users/<user_id>/delete', methods=['POST'])
# def user_delete(user_id):
#     x = request.form.get('u_id')
#     if user_id == request.form.get('u_id'): # if matches
#         requests.delete(user_url+'/user/'+user_id, headers={'x-functions-key': func_key})
#         flash("deleted 1 user")
#         return redirect(url_for("user_view"))
#     flash("delete: user_id does not match")
#     return redirect(url_for("user_view", user_id = user_id))
@app.route('/users/<user_id>/delete', methods=['POST', 'GET'])
def user_delete(user_id):
    if request.method == 'POST':
        input_id = request.form.get('confirm_delete')

        if input_id != user_id:  # Check if input_id matches the user_id from the URL
            flash("User ID does not match with ID in database")
            return redirect(url_for('user_view', user_id=user_id))

        # If IDs match, delete the user
        # logout_user(user_id)
        res = requests.delete(f"{user_url}/user/{user_id}", params={"code": func_key})

        if res.status_code == 200:  # Check if the response indicates success
            session.clear()
            flash("User deleted successfully.")
            return render_template('index.html')
            # redirect to index not working
            # return redirect(url_for('index'))  # Redirect to the user listing page
        else:
            flash("Error deleting user.")
            return redirect(url_for('user_view', user_id=user_id))
            # return redirect(render_template('delete-confirmation.html'))

    if request.method == 'GET':
        return render_template("delete-confirmation.html")


# @app.post('/user/users/<user_id>/update')
# def user_update(user_id):
#     print("updating")
#     old_pass = request.form.get("old_pass")
#     res = requests.get(user_url+'/user/' + user_id,
#                        params={"code": func_key})
#     us = json.loads(res.text)
#     password = us["password"]
#     print(password)
#     if (old_pass != password):
#         print("no match")
#         flash("old password incorrect")
#         return redirect(url_for("user_view", user_id = user_id))
#     new_pass = request.form.get("new_pass")
#     new_pass2 = request.form.get("new_pass2")
#     if (new_pass != new_pass2):
#         flash("new passwords do not match")
#         return redirect(url_for("user_view", user_id=user_id))
#     #update password
#     requests.put(user_url+'/user/'+user_id, json={
#          'password': new_pass},
#          headers={'x-functions-key': func_key});
#     flash("password updated")
#     return redirect(url_for("user_view", user_id = user_id))

@app.route('/users/<user_id>/update', methods=['POST', 'GET'])
def user_update(user_id):
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # get the old password and check to see if it matches the old password typed in. if not, flash error.

    if request.method == 'GET':
        return render_template('change-password.html', user_id=user_id)

    if request.method == 'POST':

        user_res = requests.get(f"{user_url}/user/{user_id}", params={"code": func_key})
        user_res = json.loads(user_res.text)
        old_db_pass = user_res['password']

        if old_password != old_db_pass:
            flash("Old password does not match existing password")
            return redirect(url_for('user_view', user_id=user_id))

        # check if the new passwords match
        if new_password != confirm_password:
            flash("New passwords do not match.")
            return redirect(url_for('user_view', user_id=user_id))

        # if the passwords match, update the password using json and
        update_res = requests.put(f"{user_url}/user/{user_id}", params={"code": func_key},
                                  json={"password": confirm_password})

        # make sure the response is good so you know it updates
        if update_res.status_code != 200:
            flash("Failed to update password.")
            return redirect(url_for('user_view', user_id=user_id))

        flash("Password updated successfully")
        return redirect(url_for('user_view', user_id=user_id))

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    print('loading user')
    return User.get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    # TODO: get form data and validate
    un = request.form.get("username")
    pw = request.form.get("password")


    ## authenticate
    user = User.authenticate(un, pw)

    if user:
        login_user(user)
        flash('logged in')
        res = requests.get(user_url+"/makepost/") # might break deployed version
        print(f"Response Status Code: {res.status_code}")
        print(f"Response Text: {res.text}")

        ps = json.loads(res.text)
        session['posts'] = ps
        return redirect(url_for('index')) # If posts=ps is removed this works
    else:
        flash('login unsuccessful')
        return redirect(url_for('login'))


@app.route("/logout")
@login_required # requires login to access (could use for other endpoints)
def logout():
    logout_user()
    flash('logged out')
    return redirect(url_for('index'))




@app.route('/make_post/<user_id>', methods=['GET', 'POST'])
@login_required # requires login to access (could use for other endpoints)
def make_post(user_id):
    if request.method == 'GET':
        return render_template('make-post.html')
    txt = request.form.get('post_text')
    flash("Posted: " + txt)
    res = requests.post(user_url+'/makepost/'+ user_id, json={
        'post_text': txt},
                        headers={'x-functions-key': func_key})
    res = requests.get(user_url + "/makepost/")
    ps = json.loads(res.text)
    session['posts'] = ps
    return redirect(url_for('index'))  # If posts=ps is removed this works
# Need to pass in user_id when called (in HTML?)


@app.route('/users/<user_id>/update_bio', methods=['POST', 'GET'])
@login_required
def update_bio(user_id):
    user = User.get(user_id)

    # Ensure the current user is the same as the user trying to update
    if user_id != str(current_user.id):
        flash("You can't update another user's bio!")
        return redirect(url_for('user_view', user_id=user_id))

    if request.method == 'POST':
        new_bio = request.form.get('bio')
        if new_bio:
            x = user.update_bio(user_id, new_bio)
            flash(f"Bio updated successfully! {x}")
            return redirect(url_for('user_view', user_id=user_id))
        else:
            flash("Please provide a valid bio.")

    return render_template('update-bio.html', user=user)


@app.route('/like/<post_id>', methods=['POST'])
def like(post_id):
    print("IN APP LIKE")
    res = requests.post(user_url + '/like/' + post_id, json={
        'user_id': current_user.id},
                        headers={'x-functions-key': func_key})
    return redirect(url_for('index') + f"#{post_id}")


@app.route('/delete/<post_id>', methods=['POST'])
def delete(post_id):
    print("IN APP DELETE")
    print(post_id)
    res = requests.delete(user_url + '/delete/' + post_id,
                        headers={'x-functions-key': func_key})
    flash('deleted post')
    return redirect(url_for('index'))


@app.route('/comment/<post_id>', methods=['GET'])
def view_comments(post_id):
    print("IN APP VIEW COMMENT")
    print(post_id)
    id = str(post_id)[10:-2]
    res = requests.get(user_url+'/makepost/' + id,
                           params={"code": func_key})
    post = json.loads(res.text)
    return render_template('comments.html', post=post)


@app.route('/makecomment/<post_id>', methods=['POST'])
def make_comment(post_id):
    print("IN APP MAKE COMMENT")
    print(post_id)
    id = str(post_id)[10:-2]
    txt = request.form.get('comment_text')
    res = requests.post(user_url + '/makecomment/' + id, json={
        'user_id': current_user.id, 'text': txt},
                        headers={'x-functions-key': func_key})
    flash("commented " + txt)
    return redirect(url_for('view_comments', post_id = post_id))


@app.route('/comment/delete/<post_id>/<comment_txt>', methods=['POST'])
def delete_comment(post_id, comment_txt):
    print(post_id)
    print("IN APP DELETE COMMENT" + comment_txt)
    res = requests.delete(user_url + '/comment/delete/' + str(post_id[10:-2]) + '/' + comment_txt,
                        headers={'x-functions-key': func_key})
    flash("deleted comment")
    return redirect(url_for('view_comments', post_id=post_id))

#
# @app.route('/users/<user_id>/add_friend', methods=['POST'])
# @login_required
# def add_friend(user_id):
#     # Retrieve the user to be added as a friend
#     friend_user = User.get(user_id)
#
#     if not friend_user:
#         flash("User not found.")
#         return redirect(url_for('user_view', user_id=user_id))
#
#     # Add the current user to the friend's friend list
#     if current_user.add_friend(user_id):
#         flash(f"You and {friend_user.username} are now friends!")
#     else:
#         flash("Failed to add friend.")
#
#     # Redirect back to the user's profile page
#     return redirect(url_for('user_view', user_id=user_id))
#
#
# @app.route('/users/<user_id>/remove_friend', methods=['POST'])
# @login_required
# def remove_friend(user_id):
#     # Check if the user is trying to remove themselves (this shouldn't happen)
#     if user_id == str(current_user.id):
#         flash("You cannot remove yourself as a friend.")
#         return redirect(url_for('user_view', user_id=user_id))
#     friend_user = User.get(user_id)
#     # Ensure the user is trying to remove a friend from their friends list
#     if user_id not in current_user.friends:
#         flash("This user is not in your friends list.")
#         return redirect(url_for('user_view', user_id=user_id))
#
#     # Remove the friend
#     success = current_user.remove_friend(user_id)
#
#     if success:
#         flash(f"You have removed {friend_user.username} from your friends list.")
#     else:
#         flash("There was an error removing the friend.")
#
#     # Redirect back to the user's profile
#     return redirect(url_for('user_view', user_id=user_id))


@app.route('/comment/like/<post_id>/<comment_txt>', methods=['POST'])
def like_comment(post_id, comment_txt):
    print("IN APP LIKE_COMMENT")
    res = requests.post(user_url + '/comment/like/' + str(post_id[10:-2]) + '/' + comment_txt, json={
        'user_id': current_user.id},
                          headers={'x-functions-key': func_key})
    return redirect(url_for('view_comments', post_id=post_id))


@app.route('/users/<user_id>/friend/<friend_id>', methods=['POST'])
@login_required
def add_friend(user_id, friend_id):
   print("IN USER ADD_FRIEND")
   print(user_id)
   print(friend_id)
   res = requests.post(user_url + '/user/friend/' + user_id + '/' + friend_id)
   print(res)
   return redirect(url_for('user_view', user_id=friend_id))


@app.route('/users/<user_id>/unfriend/<friend_id>', methods=['POST'])
@login_required
def remove_friend(user_id, friend_id):
   print("IN USER REMOVE_FRIEND")
   res = requests.delete(user_url + '/user/unfriend/' + user_id + '/' + friend_id)
   return redirect(url_for('user_view', user_id=friend_id))
