import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect, render_template
import time
import pandas as pd
from collections import Counter
import plotly
from bokeh.plotting import figure, show
import numpy as np

app = Flask(__name__)
app.secret_key = "acklahpossdj"
app.config['SESSION_COOKIE_NAME'] = "unnamed cookie"
TOKEN_INFO = 'token_info'
CLIENT_ID = '6d8d78cb3d284ebd8861a7c7e224288d'
CLIENT_SECRET = 'bec8b6dd39cf4d3f8f3af94f5a2f9196'
SCOPE = 'user-library-read user-top-read'

def most_common_genres(genres):
    counted = Counter(genres).most_common(5)
    common = []
    for i in counted:
        common.append(i[0])
    return common

def genre_getter(list):
    genres = []
    for item in list:
        genres += item['genres']
    return genres

def list_to_text(list):
    s = ""
    n = len(list)
    for i in range(n - 1):
        s += list[i] + ", "
    s += "and " + list[n - 1]
    s.rstrip()
    return s

def rec_songs(sp):
    #check if the song has already been listened to
    return ""

@app.route('/')
def login():
    sp_oath = create_spotify_oauth()
    auth_url = sp_oath.get_authorize_url()
    return redirect(auth_url)

@app.route('/authorize')
def authorize():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_cached_token()
    session['token_info'] = token_info
    return redirect(url_for('get_tracks', _external=True))

@app.route('/getData', methods=['GET', 'POST'])
def get_tracks():
    session['token_info'], authorized = get_token()
    session.modified = True

    if not authorized:
        return redirect('/')
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    short = sp.current_user_top_artists(limit=20, offset=0, time_range='short_term')
    short = short['items']
    global s_genres
    s_genres = genre_getter(short)
    
    medium = sp.current_user_top_artists(limit=20, offset=0, time_range='medium_term')
    medium = medium['items']
    global m_genres 
    m_genres = genre_getter(medium)

    long = sp.current_user_top_artists(limit=20, offset=0, time_range='long_term')
    long = long['items']
    global l_genres 
    l_genres = genre_getter(long)

    return render_template('data.html',
                s_genres=list_to_text(most_common_genres(s_genres)), 
                m_genres=list_to_text(most_common_genres(m_genres)), 
                l_genres=list_to_text(most_common_genres(l_genres)), 
                s_labels=list(set(s_genres)), 
                s_data=get_counts(s_genres), 
                m_labels=list(set(m_genres)), 
                m_data=get_counts(m_genres),
                l_labels=list(set(l_genres)), 
                l_data=get_counts(l_genres))


def get_counts(list):
    counted = Counter(list)
    nums = []

    for key in counted:
        nums.append(counted[key])

    return nums





# Checks to see if token is valid and gets a new token if not
def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid



def create_spotify_oauth():
    #make a new one everytime
    return (SpotifyOAuth(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri=url_for('authorize', _external=True),
        scope=SCOPE))

if __name__ == "__main__":
    app.run()







