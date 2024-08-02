import json

import requests
from flask import Blueprint
from flask import current_app
from flask import request, redirect, url_for
from flask_login import login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from oauthlib.oauth2 import WebApplicationClient

auth_blueprint = Blueprint('auth_blueprint', __name__, template_folder='templates', static_folder='static')
db = SQLAlchemy()


@auth_blueprint.route('/login', methods=['GET'])
def login():
    GOOGLE_CLIENT_ID = current_app.config.get('GOOGLE_CLIENT_ID')
    client = WebApplicationClient(GOOGLE_CLIENT_ID)

    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )

    return redirect(request_uri)


@auth_blueprint.route("/login/callback")
def callback():
    from api.models import User
    GOOGLE_CLIENT_ID = current_app.config.get('GOOGLE_CLIENT_ID')
    client = WebApplicationClient(GOOGLE_CLIENT_ID)
    GOOGLE_CLIENT_SECRET = current_app.config.get('GOOGLE_CLIENT_SECRET')
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    print(token_response.json())
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided
    # by Google
    user = User(id=unique_id, name=users_name, email=users_email, profile_pic=picture)

    # Doesn't exist? Add to database
    if not User.query.get(unique_id):
        db.session.add(user)
        db.session.commit()

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))


@auth_blueprint.route("/logout")
# @login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


def get_google_provider_cfg():
    GOOGLE_DISCOVERY_URL = current_app.config.get('GOOGLE_DISCOVERY_URL')
    return requests.get(GOOGLE_DISCOVERY_URL).json()
