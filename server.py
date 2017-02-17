#!flask/bin/python

from flask import Flask, request, Response
from gevent.pywsgi import WSGIServer
from gevent import monkey
import requests, time, json, os
from functools import wraps

monkey.patch_all()

app = Flask(__name__)
app.debug = True

def check_auth(username, password):
    global user, pass1
    user = username
    pass1 = password
    with open('credentials.json') as upfile:    
        d = json.load(upfile)
    return username == username and password == d[username]

def authenticate():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/me', methods=['GET', 'POST'])
@requires_auth
def me():
    global delay, increment
    delay = int(request.args.get('delay'))
    increment = int(request.args.get('increment'))
    print delay
    time.sleep(delay)
    
    if os.stat("test.json").st_size != 0:
        with open('test.json') as data_file:    
            data = json.load(data_file)
    else:
        data = {}

    fo = open("test.json","wb")

    if user in json.dumps(data):
        data[user] = data[user] + increment
    else:
        data[user] = increment
    fo.write(json.dumps(data))    
    fo.close()

    return json.dumps({"username": user, "delay": delay, "counter": data[user]})

def main():
    http = WSGIServer(('localhost', 8080), app.wsgi_app)
    http.serve_forever()

if __name__ == '__main__':
    main()
