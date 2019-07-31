#
# To run:
# python3 app.py
# 

from flask import Flask, render_template, request, redirect, url_for, jsonify, session#, g
from flask_login import LoginManager, login_required, login_user, logout_user
import firebase_admin
from firebase_admin import credentials, firestore
import datetime, sys, math, os, google.api_core
from user import User
import pyrebase

app = Flask(__name__)

DEBUG = True

if (DEBUG):
	import config
	serviceAccountKey = config.serviceAccountKey
	config_pyrebase = config.config_pyrebase
	app.secret_key = config.flask_secret_key
else:
	serviceAccountKey = {
		"type": "service_account",
		"project_id": "meter-image-capturing",
		"private_key_id": os.environ["private_key_id"],
		"private_key": os.environ["private_key"].replace('\\n', '\n'),
		"client_email": "firebase-adminsdk-l3mxx@meter-image-capturing.iam.gserviceaccount.com",
		"client_id": os.environ["client_id"],
		"auth_uri": "https://accounts.google.com/o/oauth2/auth",
		"token_uri": "https://oauth2.googleapis.com/token",
		"auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
		"client_x509_cert_url": os.environ["client_x509_cert_url"]
	}

	config_pyrebase = {
		"apiKey": os.environ["apiKey"],
		"authDomain": "meter-image-capturing.firebaseapp.com",
		"databaseURL": "https://meter-image-capturing.firebaseio.com",
		"storageBucket": "meter-image-capturing.appspot.com"
	}

	app.secret_key = os.environ["flask_secret_key"]

# Pyrebase credentials
firebase = pyrebase.initialize_app(config_pyrebase)

# Firebase Auth Admin credentials
cred = credentials.Certificate(serviceAccountKey)
firebase_admin.initialize_app(cred)
db = firestore.client()

DIRECTION_DESCENDING = firestore.Query.DESCENDING

@app.route('/')
def index():
	if ('UID' not in session):
		return redirect(url_for('signin'))
	else:
		return render_template('index.html')

@app.route('/signin', methods=["GET", "POST"])
def signin():
	if ('UID' not in session):
		return render_template('signin.html')
	else:
		return redirect(url_for('index'))

@app.route('/account')
def account():
	if ('UID' not in session):
		return redirect(url_for('signin'))
	else:
		return render_template('account.html', uid=session['UID'])

# Get Firebase Auth UID
@app.route('/_route_to_api', methods = ['POST'])
def api():
	session.pop('UID', None)

	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']

		# Check if UID matches UID from pyrebase wrapper.  If not then pop session['UID']
		try:
			auth = firebase.auth()
			user = auth.sign_in_with_email_and_password(email, password)
			localId = user['localId']
			if (localId != request.form['uid']) or (request.form['uid'] == ''):
				session.pop('UID', None)
			else:
				session['UID'] = localId
			return 'OK', 200
		except: #requests.exceptions.HTTPError
			session.pop('UID', None)
			return 'OK', 200

@app.route('/_logout', methods = ['POST'])
def _logout():
	if request.method == 'POST':
		session.pop('UID', None)
		return 'OK', 200

@app.route('/api', methods = ['POST'])
def apii():
	if ('UID' not in session) or ('startDate' not in session) or ('endDate' not in session):
		return 'OK', 200
	data = []
	ref = db.collection('scans')
	UID = session['UID']
	startDate = session['startDate']
	endDate = session['endDate']
	query = ref.where('uid', '==', UID).where('timestamp', '>=', startDate).where('timestamp', '<=', endDate).order_by('timestamp', direction=DIRECTION_DESCENDING).limit(5000)
	docs = query.stream()
	for doc in docs:
		dictionary = doc.to_dict()
		dictionary['timestamp'] = '{0:%I:%M%p %m/%d/%y}'.format(dictionary['timestamp'])
		data.append(dictionary)
	return _createReportString(data)

@app.route('/_apiii', methods = ['POST'])
def apiii():
	if ('UID' not in session):
		return 'OK', 200

	if request.method == 'POST':
		UID = session['UID']
		startDate = _parseDate(request.form['startDate'])
		endDate = _parseDate(request.form['endDate'])
		session['startDate'] = startDate
		session['endDate'] = endDate
		data = []
		ref = db.collection('scans')
		query = ref.where('uid', '==', UID).where('timestamp', '>=', startDate).where('timestamp', '<=', endDate).order_by('timestamp', direction=DIRECTION_DESCENDING).limit(5000)
		docs = query.stream()
		count = 1
		for doc in docs:
			dictionary = doc.to_dict()
			dictionary['timestamp'] = '{0:%I:%M%p %m/%d/%y}'.format(dictionary['timestamp'])
			dictionary['index'] = count
			data.append(dictionary)
			count += 1
		return jsonify(data)

'''@app.route('/add_new_record', methods = ['POST'])
def add_new_record():
	if request.method == 'POST':
		print("add new record")
		result = request.form.to_dict()
		result['timestamp'] = datetime.datetime.now()
		result['uid'] = UID
		try:
			db.collection('scans').add(result)
		except google.api_core.exceptions.ServiceUnavailable:
			print(sys.exc_info()[0], ' occured.')
			db.collection('scans').add(result)
		return redirect(url_for('index'))'''

def _createReportString(scans):
	ret = "'machine_id', 'progressive_1', 'progressive_2', 'progressive_3', 'progressive_4',"
	ret += " 'progressive_5', 'progressive_6', 'notes', 'timestamp', 'user'\n"
	for scan in scans:
		ret += "'" + str(scan['machine_id']) + "', '" + str(scan['progressive1']) + "', '" 
		ret += str(scan['progressive2']) + "', '" + str(scan['progressive3']) + "', '" 
		ret += str(scan['progressive4']) + "', '" + str(scan['progressive5']) + "', '" 
		ret += str(scan['progressive6']) + "', '" + str(scan['notes']) + "', '" + str(scan['timestamp']) 
		ret += "', '" + str(scan['userName']) + "'\n"
	return ret

def _parseDate(date):
	# date format: '2019-07-31:12:59:PM'
	year = int(date[0:4])
	month = int(date[5:7])
	day = int(date[8:10])
	am_pm = date[17:19]
	hour = int(date[11:13]) - 1 #Subtract 1 or not?
	minute = int(date[14:16])
	am_pm = date[17:19]
	if am_pm == 'PM':
		hour += 12

	return datetime.datetime(year, month, day, hour=hour, minute=minute)

'''
@app.before_request
def before_request():
	if not 'EMAIL' in session:
		return redirect(url_for('signin'))
'''

if __name__ == '__main__':
	
	HOST = '127.0.0.1'
	PORT = 5000
	THREADED = True
	app.run(host=HOST, port=PORT, debug=DEBUG)

	'''sample = { 'machine_id': '12345678', 
		'progressive_1': '123.45', 
		'progressive_2': '87.37', 
		'progressive_3': '55.50', 
		'progressive_4': '25.13', 
		'progressive_5': '', 
		'progressive_6': '', 
		'timestamp': datetime.datetime.now(), 
		'notes': '', 
		'user': 'Alex', 
		'uid': 'qEqNIQlYEONuG8EMg3IFatXRpIJ2'
	}

	for i in range(2):
		print(i)
		db.collection('scans').document().set(sample)'''












