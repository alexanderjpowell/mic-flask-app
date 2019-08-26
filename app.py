#
# To run:
# source env/bin/activate (if using local virtual environment)
# python3 app.py
# 

from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from werkzeug import secure_filename
import firebase_admin
from firebase_admin import credentials, firestore
import sys, math, os, google.api_core, csv, string, random
from datetime import datetime, timedelta
import pyrebase

UPLOAD_FOLDER = os.getcwd() + '/files'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

DEBUG = False

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
		session.pop('startDate', None)
		session.pop('endDate', None)
		session.pop('timeZoneOffset', None)
		return render_template('index.html')
	#return render_template('index.html')

@app.route('/signin')#, methods=["GET", "POST"])
def signin():
	if ('UID' not in session):
		return render_template('signin.html')
	else:
		return redirect(url_for('index'))
	#return render_template('signin.html')

@app.route('/account')
def account():
	if ('UID' not in session):
		return redirect(url_for('signin'))
	else:
		return render_template('account.html', email=session['email'], name=session['displayName'])

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
				session['email'] = user['email']
				session['displayName'] = user['displayName']
			return 'OK', 200
		except: #requests.exceptions.HTTPError
			session.pop('UID', None)
			return 'OK', 200

@app.route('/_logout', methods = ['POST'])
def _logout():
	if request.method == 'POST':
		session.clear()
		return 'OK', 200

@app.route('/api', methods = ['POST'])
def apii():
	if ('UID' not in session) or ('startDate' not in session) or ('endDate' not in session) or ('timeZoneOffset' not in session):
		return 'OK', 200
	UID = session['UID']
	offset = session['timeZoneOffset']
	startDate = session['startDate']
	endDate = session['endDate']
	return _createReportString(_fetchRecordsFromDatabase(UID, offset, startDate, endDate))

@app.route('/_apiii', methods = ['POST'])
def apiii():
	if ('UID' not in session):
		return 'OK', 200
	if request.method == 'POST':
		UID = session['UID']
		offset = int(request.form['timeZoneOffset'])
		startDate = _parseDate(request.form['startDate'], offset)
		endDate = _parseDate(request.form['endDate'], offset)
		session['startDate'] = startDate
		session['endDate'] = endDate
		session['timeZoneOffset'] = offset
		return jsonify(_fetchRecordsFromDatabase(UID, offset, startDate, endDate))

@app.route('/upload', methods = ['GET', 'POST'])
def upload_file():
	if ('UID' not in session):
		return 'OK', 200
	if request.method == 'GET':
		return render_template('upload.html')
	if request.method == 'POST':
		checkIfTempDirExists()

		if 'file' not in request.files:
			return render_template('account.html')
		
		f = request.files['file']
		
		if f.filename == '':
			return render_template('account.html')
		
		if f and allowed_file(f.filename):
			filename = secure_filename(f.filename)
			f.save(os.path.join(UPLOAD_FOLDER, filename))

			try:
				file = open(UPLOAD_FOLDER + '/' + filename, 'r')
				reader = csv.reader(file)
				_processFile(reader)
			except Exception as ex:
				#print(str(ex))
				flash('Error reading file: only .csv files accepted. Try again.', 'error')
				return render_template('upload.html')

			file.close()
			f.close()
			os.remove(UPLOAD_FOLDER + '/' + filename)
			flash('File uploaded successfully!', 'success')
			return render_template('upload.html')

		flash('Error reading file: only .csv files accepted. Try again.', 'error')
		return render_template('upload.html')

def checkIfTempDirExists():
	if not os.path.exists(UPLOAD_FOLDER):
		os.mkdir(UPLOAD_FOLDER)

def _fetchRecordsFromDatabase(UID, offset, startDate, endDate):
	data = []
	ref = db.collection('scans')
	query = ref.where('uid', '==', UID).where('timestamp', '>=', startDate).where('timestamp', '<=', endDate) \
		.order_by('timestamp', direction=DIRECTION_DESCENDING).limit(5000)
	docs = query.stream()
	index = 1
	for doc in docs:
		dictionary = doc.to_dict()
		dictionary['timestamp'] = _convertDateToLocal(dictionary['timestamp'], offset)
		#dictionary['timestamp'] = '{0:%I:%M%p %m/%d/%y}'.format(dictionary['timestamp'])
		dictionary['timestamp'] = str(dictionary['timestamp'])
		dictionary['index'] = index
		data.append(dictionary)
		index += 1
	return data

'''@app.route('/_add_new_record', methods = ['POST'])
def add_new_record():
	if ('UID' not in session) or ('email' not in session):
		return 'OK', 400
	if request.method == 'POST':
		result = request.form.to_dict()
		result['timestamp'] = firestore.SERVER_TIMESTAMP
		result['uid'] = session['UID']
		result['email'] = session['email']

		try:
			print(result)
			#db.collection('scans').add(result)
		except google.api_core.exceptions.ServiceUnavailable:
			print(sys.exc_info()[0], ' occured.')
			#db.collection('scans').add(result)
		return redirect(url_for('index'))
		#return 'OK', 400'''

'''@app.before_request
def before_request():
	if ('UID' not in session) and (request.endpoint != 'signin'):
		return redirect(url_for('signin'))'''

def _convertDateToLocal(date, offset):
	year = date.year
	month = date.month
	day = date.day
	hour = date.hour
	minute = date.minute
	second = date.second

	time = datetime(year, month, day, hour=hour, minute=minute, second=second)
	delta = timedelta(hours=offset)
	return time - delta

def _parseDate(date, offset):
	# date format: '2019-07-31:12:59:PM'
	year = int(date[0:4])
	month = int(date[5:7])
	day = int(date[8:10])
	am_pm = date[17:19]
	hour = int(date[11:13])
	minute = int(date[14:16])
	am_pm = date[17:19]
	if ((am_pm == 'AM') and (hour == 12)):
		hour = 0
	elif ((am_pm == 'PM') and (hour != 12)):
		hour += 12

	time = datetime(year, month, day, hour=hour, minute=minute)
	delta = timedelta(hours=offset)
	return time + delta

def _createReportString(scans):
	ret = '"Machine","Progressive1","Progressive2","Progressive3","Progressive4","Progressive5","Progressive6","Notes","Date","User"\n'
	for scan in scans:
		ret += '"' + str(scan['machine_id']) + '","' + str(scan['progressive1']) + '","' 
		ret += str(scan['progressive2']) + '","' + str(scan['progressive3']) + '","' 
		ret += str(scan['progressive4']) + '","' + str(scan['progressive5']) + '","' 
		ret += str(scan['progressive6']) + '","' + str(scan['notes']) + '","' + str(scan['timestamp']) 
		ret += '","' + str(scan['userName']) + '"\n'
	return ret

def _insertToDatabase(location, machine_id, description, progressive_count, user):
	query = db.collection('formUploads/' + session['UID'] + '/uploadFormData')
	data = {
		'location' : location, 
		'machine_id' : machine_id, 
		'description' : description, 
		'progressive_count' : progressive_count, 
		'user' : user, 
		'completed' : False,
		'timestamp' : firestore.SERVER_TIMESTAMP
	}
	query.document().set(data)

def _processFile(lines):
	# Delete existing collection, if necessary
	coll_ref = db.collection('formUploads/' + session['UID'] + '/uploadFormData')
	_delete_collection(coll_ref, 50)
	# Check header
	header = next(lines)
	required_fields = {'location', 'machine_id', 'description'}
	if not set(required_fields).issubset(header):
		raise Exception('Missing required header field(s)', 400)

	locationIndex = header.index('location')
	machineIdIndex = header.index('machine_id')
	descriptionIndex = header.index('description')
	displayNames = _get_users()

	for line in lines:
		location = line[locationIndex]
		machine_id = line[machineIdIndex]
		description = line[descriptionIndex]
		if 'progressive_count' in header:
			progressive_count = line[header.index('progressive_count')]
		else:
			progressive_count = None

		if 'user' in header:
			user = line[header.index('user')]
		else:
			user = None
		
		'''if len(displayNames):
			user = random.sample(displayNames, 1)[0]
		else: # no users on this account
			user = None'''
		_insertToDatabase(location, machine_id, description, progressive_count, user)

def _get_users():
	displayNamesRef = db.collection('users/' + session['UID'] + '/displayNames')
	docs = displayNamesRef.stream()
	sett = set()
	for doc in docs:
		sett.add(doc.get('displayName'))
	return sett

def _delete_collection(coll_ref, batch_size):
	docs = coll_ref.limit(batch_size).stream()
	deleted = 0

	for doc in docs:
		doc.reference.delete()
		deleted = deleted + 1

	if deleted >= batch_size:
		return _delete_collection(coll_ref, batch_size)

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
	
	HOST = '127.0.0.1'
	PORT = 5000
	app.run(host=HOST, port=PORT, debug=DEBUG)










