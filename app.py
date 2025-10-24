import os
from flask import Flask, render_template, request, redirect, url_for, flash
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'change-me')

SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

use_spotipy = bool(SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET)
if use_spotipy:
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        ))
    except Exception as e:
        sp = None
        use_spotipy = False
else:
    sp = None

@app.route('/')
def index():
    return render_template('index.html', creds_ok=use_spotipy)

@app.route('/search')
def search():
    q = request.args.get('q','').strip()
    if not q:
        flash('Please enter a search term.', 'warning')
        return redirect(url_for('index'))

    if not use_spotipy or sp is None:
        flash('Spotify credentials not configured. See README to get API keys.', 'danger')
        return render_template('search.html', query=q, tracks=[] , creds_ok=False)

    try:
        results = sp.search(q=q, limit=12, type='track')
        tracks = results.get('tracks', {}).get('items', [])
    except Exception as e:
        flash('Error querying Spotify API: {}'.format(e), 'danger')
        tracks = []
    return render_template('search.html', query=q, tracks=tracks, creds_ok=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
