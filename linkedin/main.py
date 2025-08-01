import os
import requests
from flask import Flask, redirect, request, session, url_for
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# LinkedIn config
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPES = "w_member_social rw_organization_admin w_organization_social"

@app.route('/')
def index():
    return '<a href="/login">Login with LinkedIn</a>'

@app.route('/login')
def login():
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&scope={SCOPES}&state=123456"
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Error: No code returned from LinkedIn", 400

    # Exchange code for access token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    response = requests.post(token_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    token_json = response.json()

    if "access_token" not in token_json:
        return f"Error fetching token: {token_json}"

    access_token = token_json["access_token"]
    session["access_token"] = access_token

    return f"Access token received: {access_token}<br><br><a href='/me'>View LinkedIn Profile Info</a>"

@app.route('/me')
def me():
    access_token = session.get("access_token")
    if not access_token:
        return redirect(url_for('login'))

    profile_url = "https://api.linkedin.com/v2/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get(profile_url, headers=headers)

    return res.json()

if __name__ == '__main__':
    app.run(debug=True)
