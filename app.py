#
# To run:
# python3 app.py
# 

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, login_required, login_user, logout_user
import firebase_admin
from firebase_admin import credentials, firestore
import datetime, sys, math, os, google.api_core
from user import User
import pyrebase

app = Flask(__name__)

#app.secret_key = 'keep-this-secret'
#login_manager = LoginManager()
#login_manager.init_app(app)

DEBUG = False

if (False):
	import config
	serviceAccountKey = config.serviceAccountKeyDebug
	config_pyrebase = config.config_pyrebase_debug
else:
	import config
	serviceAccountKey = config.serviceAccountKey
	config_pyrebase = config.config_pyrebase
	'''serviceAccountKey = {
		"type": "service_account",
		"project_id": os.environ["project_id"],
		"private_key_id": os.environ["private_key_id"],
		"private_key": os.environ["private_key"].replace('\\n', '\n'),
		"client_email": os.environ["client_email"],
		"client_id": os.environ["client_id"],
		"auth_uri": os.environ["auth_uri"],
		"token_uri": os.environ["token_uri"],
		"auth_provider_x509_cert_url": os.environ["auth_provider_x509_cert_url"],
		"client_x509_cert_url": os.environ["client_x509_cert_url"],
	}

	config_pyrebase = {
		"apiKey": os.environ['apiKey'],
		"authDomain": os.environ['authDomain'],
		"databaseURL": os.environ['databaseURL'],
		"storageBucket": os.environ['storageBucket']
	}'''

# Pyrebase credentials
firebase = pyrebase.initialize_app(config_pyrebase)

# Firebase Auth Admin credentials
cred = credentials.Certificate(serviceAccountKey)
firebase_admin.initialize_app(cred)
db = firestore.client()

DIRECTION_DESCENDING = firestore.Query.DESCENDING
PAGE_SIZE = 20
data = []
LAST_DOCUMENT_SNAPSHOT = None
UID = None
#UID = 'qEqNIQlYEONuG8EMg3IFatXRpIJ2'
#UID = 'xgdRnVu3yrgjEhrMQgDSImBEOCc2'
count = 1

#user = None

@app.route('/')
def index():
	global UID
	global data
	global LAST_DOCUMENT_SNAPSHOT
	#global user

	#user = User('qEqNIQlYEONuG8EMg3IFatXRpIJ2')
	
	if (UID == None):
		return redirect(url_for('signin'))
	else:
		return render_template('index.html')

@app.route('/signin', methods=["GET", "POST"])
def signin():
	global UID

	if (UID == None):
		return render_template('signin.html')
	else:
		return redirect(url_for('index'))

@app.route('/account')
def account():
	global UID

	if (UID == None):
		return redirect(url_for('signin'))
	else:
		return render_template('account.html', uid=UID)

# Get Firebase Auth UID
@app.route('/_route_to_api', methods = ['POST'])
def api():
	global UID

	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']

		# Check if UID matches UID from pyrebase wrapper.  If not then set UID to None
		try:
			auth = firebase.auth()
			user = auth.sign_in_with_email_and_password(email, password)
			localId = user['localId']
			if (localId != request.form['uid']) or (request.form['uid'] == ''):
				UID = None
			else:
				UID = request.form['uid']
			return 'OK', 200
		except: #requests.exceptions.HTTPError
			UID = None
			return 'OK', 200

@app.route('/_logout', methods = ['POST'])
def _logout():
	global UID

	if request.method == 'POST':
		if request.form['uid'] == '':
			UID = None
		return 'OK', 200

@app.route('/api', methods = ['POST'])
def apii():
	#global user
	if UID == None:
		return 'OK', 200
	
	return _createReportString(data)

@app.route('/_apiii', methods = ['POST'])
def apiii():
	global UID
	global data
	global LAST_DOCUMENT_SNAPSHOT
	global count

	if UID == None:
		return 'OK', 200

	if request.method == 'POST':
		startDate = _parseDate(request.form['startDate'])
		endDate = _parseDate(request.form['endDate'])
		#LAST_DOCUMENT_SNAPSHOT = None
		data.clear()
		ref = db.collection('scans')
		query = ref.where('uid', '==', UID).where('timestamp', '>=', startDate).where('timestamp', '<=', endDate).order_by('timestamp', direction=DIRECTION_DESCENDING)
		docs = query.stream()
		count = 1
		for doc in docs:
			LAST_DOCUMENT_SNAPSHOT = doc
			dictionary = doc.to_dict()
			dictionary['timestamp'] = '{0:%I:%M%p %m/%d/%y}'.format(dictionary['timestamp'])
			dictionary['index'] = count
			data.append(dictionary)
			count += 1
		return jsonify(data)

'''@app.route('/_fetch_more_records', methods = ['POST'])
def _fetch_more_records():
	global LAST_DOCUMENT_SNAPSHOT
	global count
	
	new_data = []
	ref = db.collection('scans')
	query = ref.where('uid', '==', UID).order_by('timestamp', direction=DIRECTION_DESCENDING).start_after(LAST_DOCUMENT_SNAPSHOT).limit(PAGE_SIZE)
	docs = query.stream()
	for doc in docs:
		LAST_DOCUMENT_SNAPSHOT = doc
		dictionary = doc.to_dict()
		dictionary['timestamp'] = '{0:%I:%M%p %m/%d/%y}'.format(dictionary['timestamp'])
		dictionary['index'] = count
		data.append(dictionary)
		new_data.append(dictionary)
		count += 1
	return jsonify(new_data)'''

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

	'''print("year: " + str(year))
	print("month: " + str(month))
	print("day: " + str(day))
	print("am_pm: " + am_pm)
	print("hour: " + str(hour))
	print("minute: " + str(minute))'''

	return datetime.datetime(year, month, day, hour=hour, minute=minute)

'''@login_manager.user_loader
def load_user(userid):
	return User(userid)'''

if __name__ == '__main__':
	
	HOST = '127.0.0.1'
	PORT = 5000
	USE_RELOADER = True
	app.run(host=HOST, port=PORT, debug=DEBUG, use_reloader=USE_RELOADER)

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












