client_id = "375561028410-7tccvqg4aaks56svopgkc0mtqj0jn3qf.apps.googleusercontent.com"
client_secret = "LhpL1PuykglkQY6Wu_DnjfG2"
redirect_url = "a"#url

authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
token_url = "https://accounts.google.com/o/oauth2/v2/auth"
scope = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

from requests_oauthlib import OAuth2Session
google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
