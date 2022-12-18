import requests
from datetime import datetime
from flask import Flask, request, redirect, url_for, session
from flask import render_template
from flask_oauth import OAuth

host = 'lioncoursedatabase.c5zzynku9kw4.us-east-2.rds.amazonaws.com'
database_user_id = 'LionCourseAdmin'
database_user_password = 'Rivendell'
default_scheme = '6156_Project'

# Microservices URL
slave1_url = 'http://18.218.200.249:5000'
slave2_url = 'http://54.174.170.119:5000'
slave3_url = 'http://3.140.241.0:5000'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Rivendell'

oauth = OAuth()
GOOGLE_CLIENT_ID = "604932245172-af2apa8g3sr5fa7rbivsb7744qaljtp6.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
REDIRECT_URI = '/callback'  # one of the Redirect URIs from Google APIs console
google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                        #   request_token_params={'scope': 'openid profile https://www.googleapis.com/auth/userinfo.email',
                          request_token_params={'scope': 'openid https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)

# Read the value from login function
MY_EMAIL = 'xh2510@columbia.edu'
# Routes and functions

# Homepage
@app.route('/')
def welcome_page():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    return render_template('welcome.html', data=session.get('resp_obj'))

@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    session['resp_obj'] = resp
    return redirect(url_for('welcome_page'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')

# Main Functions and Features 

# redirect to search page without search key
@app.route('/search_page')
def search_page_null():
    query_output = [] # null input
    return render_template('search_page.html', data = query_output)

@app.route('/search', methods=['POST','GET'])
def search():
    json_data = request.get_json()
    return redirect(url_for('search_page', search_key = json_data))

# submitted search keywords
@app.route('/search_page/<search_key>')
def search_page(search_key):
    result = requests.get(f'{slave1_url}/search/{search_key}')
    return render_template('search_page.html', data = result.json())

wish_list =[]
# submitted planner's search keywords and return qualified search res
@app.route('/planner_page/<search_key>')
def planner_search(search_key):
    wish_list_string = '&'.join(map(str,wish_list))
    params = search_key + "@" + wish_list_string
    result = requests.get(f'{slave1_url}/plan/{params}')
    wish_list_info = requests.get(f'{slave1_url}/plan/{params}/wish_list')
    return render_template('planner_page.html', data = result.json(), wish_list = wish_list_info.json())

# redirect to planner
@app.route('/planner_page')
def planner_page():
    # result = requests.get(f'{slave1_url}/search/{search_key}')
    query_output = [] # null input
    wish_list_info = []
    return render_template('planner_page.html', data = query_output, wish_list = wish_list_info)

# add to wish list
@app.route('/add_course', methods=['POST','GET'])
def add_course():
    course_number = request.get_json()
    wish_list.append(course_number)
    return ('', 204)

# remove from wish list
@app.route('/remove_course', methods=['POST','GET'])
def remove_course():
    course_number = request.get_json()
    wish_list.remove(course_number)
    return ('', 204)

@app.route('/rating', methods=['POST','GET'])
def rating():
    query = request.get_json()
    search_key, evaluation = query['search_key'], query['evaluation']
    evaluation = '&'.join(str(e) for e in evaluation)
    result = requests.post(f'{slave2_url}/rating/{search_key}/{evaluation}')
    print(result.text)
    return redirect('../evaluation_page/' + search_key)

# submitted search keywords
@app.route('/evaluation_page/<search_key>')
def evaluation_page(search_key):
    result = requests.get(f'{slave2_url}/rating/{search_key}')
    return render_template('evaluation_page.html', data = result.json())

@app.route('/rating_page/<search_key>')
def rating_page(search_key):
    result = requests.get(f'{slave2_url}/rating/{search_key}')
    return render_template('rating_page.html', data = result.json())


@app.route('/message')
def message():
    result = requests.get(f'{slave3_url}/message')
    return render_template('message.html', message = result.json())

@app.route('/message/<email>')
def message_by_email(email):
    result = requests.get(f'{slave3_url}/message/{email}')
    return render_template('message.html', message = result.json())

@app.route('/message/post/<message_content>')
def post_message(message_content):
    time = datetime.now()
    result = requests.post(f'{slave3_url}/message/{MY_EMAIL}/{time}/{message_content}')
    return redirect(url_for('message'))

@app.route('/about_page')
def about_page():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    return render_template('about.html', data=session.get('resp_obj'))

if __name__ == '__main__':
    app.run(debug = True, ssl_context=('cert.pem', 'key.pem'), host='0.0.0.0', port=5000)
