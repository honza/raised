import os
import urlparse
from oauth.oauth import OAuthToken
from django.shortcuts import redirect, render_to_response
from django.conf import settings
import redis
from dropbox import client, session

APP_KEY = getattr(settings, 'DROPBOX_KEY')
APP_SECRET = getattr(settings, 'DROPBOX_SECRET')
CALLBACK = getattr(settings, 'DROPBOX_CALLBACK')
ACCESS_TYPE = getattr(settings, 'DROPBOX_ACCESS_TYPE')


if os.environ.has_key('REDISTOGO_URL'):
    urlparse.uses_netloc.append('redis')
    url = urlparse.urlparse(os.environ['REDISTOGO_URL'])
    REDIS = redis.Redis(host=url.hostname, port=url.port, db=0, password=url.password)
else:
    REDIS = redis.Redis(host='localhost', port=6379, db=0)


# Helper functions

def get_session():
    """
    Create a Dropbox session object
    """
    return session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)


def get_client(access_token):
    """
    Create a client instance based on an access_token
    """
    sess = get_session()
    sess.set_token(access_token.key, access_token.secret)
    return client.DropboxClient(sess)


def get_access_token_for_uid(uid):
    """
    Find an access token for a user
    """
    s = REDIS.get('ac:%s' % uid)
    return OAuthToken.from_string(s)


def get_urls_from_contents(dropbox_client, contents):
    """
    Return a list of temporary urls for the contents of the app folder
    """
    paths = [c['path'] for c in contents]
    urls = []
    for path in paths:
        urls.append(dropbox_client.media(path)['url'])
    return urls


# Views


def home(request):
    uid = request.session.get('uid')
    if not uid:
        return render_to_response('auth.html', {})
    else:
        access_token = get_access_token_for_uid(uid)
        c = get_client(access_token)
        folder_metadata = c.metadata('/')
        contents = folder_metadata['contents']
        urls = get_urls_from_contents(c, contents)

        return render_to_response('main.html', {
            'user': c.account_info(),
            'contents': urls
        })


def auth(request):
    sess = get_session()
    request_token = sess.obtain_request_token()
    REDIS.set('rt:%s' % request_token.key, request_token.to_string())
    url = sess.build_authorize_url(request_token, oauth_callback=CALLBACK)
    return redirect(url)


def callback(request):
    sess = get_session()

    dropbox_uid = request.GET.get('uid', None)
    oauth_token = request.GET.get('oauth_token', None)

    request_token = REDIS.get('rt:%s' % oauth_token)
    request_token = OAuthToken.from_string(request_token)

    access_token = sess.obtain_access_token(request_token)
    REDIS.set('ac:%s' % dropbox_uid, access_token.to_string())

    request.session['uid'] = dropbox_uid

    return redirect('home')


def logout(request):
    del request.session['uid']
    return redirect('home')
