from flask import Flask, redirect, url_for, session, request, jsonify
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.session import SessionStorage
import os
import requests

app = Flask(__name__)
app.secret_key = 'andewalaburger'

# Google OAuth configuration
google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
# Configure Google OAuth with flask-dance
blueprint = make_google_blueprint(
    client_id=google_client_id,
    client_secret=google_client_secret,
scope=["openid", 
           "https://www.googleapis.com/auth/userinfo.profile", 
           "https://www.googleapis.com/auth/userinfo.email"],
    redirect_to="index",  # Where to redirect after authorization
    # Important: Don't set a custom redirect_url unless necessary
)
app.register_blueprint(blueprint, url_prefix="/login")

@app.route('/')
def index():
    if google.authorized:
        resp = google.get("/oauth2/v1/userinfo")
        if resp.ok:
            user_info = resp.json()
            return jsonify({'data': user_info})
    return 'Hello! Log in with your Google account: <a href="/login/google">Log in</a>'

# This route will be automatically handled by Flask-Dance
# but adding it for clarity - you don't need to implement it yourself
# @app.route('/login/google/authorized')
# def google_authorized():
#     return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # Proper way to logout with flask-dance
    token = blueprint.token
    if token:
        # Revoke the token
        resp = google.post(
            "https://accounts.google.com/o/oauth2/revoke",
            params={"token": token["access_token"]},
        )
        
    # Clear session
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Print the expected callback URL for Google OAuth
    with app.app_context():
        print("="*80)
        print(f"Expected Google OAuth callback URL: http://127.0.0.1:5000/login/google/authorized")
        print("Make sure this exact URL is registered in your Google Cloud Console")
        print("="*80)
        
    # Required for Google OAuth to work with http://127.0.0.1
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True)