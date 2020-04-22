#
# To run:
# source env/bin/activate (if using local virtual environment)
# python3 app.py
# 

from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from werkzeug.utils import secure_filename
import firebase_admin
from firebase_admin import credentials, firestore
import sys, math, os, google.api_core, csv, string, random
from datetime import datetime, timedelta
import pyrebase
from google.cloud import storage
import json

UPLOAD_FOLDER = os.getcwd() + '/files'
SERVICE_ACCOUNT_KEYS_FOLDER = os.getcwd() + '/service_account_keys'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # Limits files to 16 megabytes

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
	if ('UID' not in session) or ('email' not in session):
		return redirect(url_for('signin'))
	else:
		session.pop('startDate', None)
		session.pop('endDate', None)
		session.pop('timeZoneOffset', None)
		return render_template('index.html')

@app.route('/_send_account_info', methods = ['POST'])
def _send_account_info():
	if request.method == 'POST':
		if ('UID' not in session):
			return render_template('signin.html')
		else:
			try:
				ret = {}
				casinos = []
				count = 0
				docs = db.collection('admins').document(session['email']).collection('casinos').stream()
				for doc in docs:
					uid = doc.id
					doc = doc.to_dict()
					dic = {}
					dic['uid'] = uid
					dic['name'] = doc['casinoName']
					casinos.append(dic)
					count = count + 1
				ret['isAdmin'] = (count > 0)
				ret['casinos'] = casinos
				return ret
			except:
				return { 'isAdmin' : False }
	return { 'isAdmin' : False }

@app.route('/signin')
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
		except:
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
	if request.method == 'POST':
		UID = session['UID']
		offset = session['timeZoneOffset']
		startDate = session['startDate']
		endDate = session['endDate']
		print('session: ')
		print(session)
		print('request.form: ')
		print(request.form)
		if 'uid' in request.form: # Admin mode
			return _create_report_string(_fetchRecordsFromDatabase(request.form['uid'], offset, startDate, endDate))
		else:
			return _create_report_string(_fetchRecordsFromDatabase(UID, offset, startDate, endDate))

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
		if 'uid' in request.form: # Admin mode
			return jsonify(_fetchRecordsFromDatabase(request.form['uid'], offset, startDate, endDate))
		else:
			return jsonify(_fetchRecordsFromDatabase(UID, offset, startDate, endDate))

@app.route('/upload', methods = ['GET', 'POST'])
def upload_file():
	checkIfTempDirsExists()
	#
	credentialFileName = os.path.join(SERVICE_ACCOUNT_KEYS_FOLDER, session['UID'] + '.json')
	credentialFile = open(credentialFileName, 'w+')
	credentialFile.write(json.dumps(serviceAccountKey))
	credentialFile.close()
	#
	if ('UID' not in session):
		return 'OK', 200
	if request.method == 'GET':
		return render_template('upload.html')
	if request.method == 'POST':

		if 'file' not in request.files:
			return render_template('upload.html')
		
		f = request.files['file']
		
		if f.filename == '':
			return render_template('upload.html')
		
		if f and allowed_file(f.filename):
			filename = secure_filename(f.filename)
			f.save(os.path.join(UPLOAD_FOLDER, filename))

			try:
				#
				#
				bucket_name = "meter-image-capturing.appspot.com"
				storage_client = storage.Client.from_service_account_json(credentialFileName)
				bucket = storage_client.bucket(bucket_name)
				destination_blob_name = session['UID'] + '.csv'
				blob = bucket.blob(destination_blob_name)
				blob.upload_from_filename(os.path.join(UPLOAD_FOLDER, filename))
				#file = open(UPLOAD_FOLDER + '/' + filename, 'r', encoding='utf8', errors='ignore')
				#reader = csv.reader(file)
				#_process_file(reader)
			except Exception as ex:
				print(str(ex))
				flash(str(ex), 'error')
				return render_template('upload.html')

			#file.close()
			f.close()
			os.remove(UPLOAD_FOLDER + '/' + filename)
			flash('File uploaded successfully!', 'success')
			return render_template('upload.html')

		flash('Error reading file: only .csv files accepted. Try again.', 'error')
		return render_template('upload.html')

def checkIfTempDirsExists():
	if not os.path.exists(UPLOAD_FOLDER):
		os.mkdir(UPLOAD_FOLDER)
	if not os.path.exists(SERVICE_ACCOUNT_KEYS_FOLDER):
		os.mkdir(SERVICE_ACCOUNT_KEYS_FOLDER)

'''
Returns a list of dictionaries
'''
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

@app.route('/_add_new_record', methods = ['POST'])
def add_new_record():
	if ('UID' not in session) or ('email' not in session):
		return 'OK', 400
	if request.method == 'POST':
		result = request.form.to_dict()
		result['timestamp'] = firestore.SERVER_TIMESTAMP
		result['uid'] = session['UID']
		result['email'] = session['email']

		try:
			#print(result)
			reference = db.collection('scans').add(result)

			#
			# First get the document id of the reference
			result.pop('uid')
			result.pop('email')
			docId = reference[1].id
			db.collection('users').document(session['UID']).collection('scans').add(result, docId)
			#
		except google.api_core.exceptions.ServiceUnavailable:
			print(sys.exc_info()[0], ' occured.')
			reference = db.collection('scans').add(result)

			#
			# First get the document id of the reference
			result.pop('uid')
			result.pop('email')
			docId = reference[1].id
			db.collection('users').document(session['UID']).collection('scans').add(result, docId)
			#
		return redirect(url_for('index'))

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

def _create_report_string(scans):
	ret = '"Machine","Progressive1","Progressive2","Progressive3","Progressive4","Progressive5","Progressive6","Progressive7","Progressive8","Progressive9","Progressive10","Notes","Date","User","Location"\n'
	for scan in scans:

		machine_id = str(scan['machine_id']) if 'machine_id' in scan else ""
		progressive1 = str(scan['progressive1']) if 'progressive1' in scan else ""
		progressive2 = str(scan['progressive2']) if 'progressive2' in scan else ""
		progressive3 = str(scan['progressive3']) if 'progressive3' in scan else ""
		progressive4 = str(scan['progressive4']) if 'progressive4' in scan else ""
		progressive5 = str(scan['progressive5']) if 'progressive5' in scan else ""
		progressive6 = str(scan['progressive6']) if 'progressive6' in scan else ""
		progressive7 = str(scan['progressive7']) if 'progressive7' in scan else ""
		progressive8 = str(scan['progressive8']) if 'progressive8' in scan else ""
		progressive9 = str(scan['progressive9']) if 'progressive9' in scan else ""
		progressive10 = str(scan['progressive10']) if 'progressive10' in scan else ""
		notes = str(scan['notes']) if 'notes' in scan else ""
		timestamp = str(scan['timestamp']) if 'timestamp' in scan else ""
		userName = str(scan['userName']) if 'userName' in scan else ""
		location = str(scan['location']) if 'location' in scan else ""

		ret += '"' + machine_id + '","' + progressive1 + '","' 
		ret += progressive2 + '","' + progressive3 + '","' 
		ret += progressive4 + '","' + progressive5 + '","' 
		ret += progressive6 + '","' + progressive7 + '","' + progressive8 + '","' + progressive9 + '","' + progressive10 + '","' + notes + '","' + timestamp 
		ret += '","' + userName + '","' + location + '"\n'

	return ret

def _insert_to_database(uid, location, machine_id, description, progressive_count, user, progressive_titles):
	query = db.collection('formUploads/' + uid + '/uploadFormData')
	data = {
		'location' : location, 
		'machine_id' : machine_id, 
		'description' : description, 
		'progressive_count' : progressive_count, 
		'user' : user, 
		'p_1' : progressive_titles[0], 
		'p_2' : progressive_titles[1], 
		'p_3' : progressive_titles[2], 
		'p_4' : progressive_titles[3], 
		'p_5' : progressive_titles[4], 
		'p_6' : progressive_titles[5], 
		'p_7' : progressive_titles[6], 
		'p_8' : progressive_titles[7], 
		'p_9' : progressive_titles[8], 
		'p_10' : progressive_titles[9], 
		'completed' : False,
		'timestamp' : firestore.SERVER_TIMESTAMP
	}
	query.document().set(data)

def _process_file(uid, lines):
	# Delete existing collection, if necessary
	coll_ref = db.collection('formUploads/' + uid + '/uploadFormData')
	_delete_collection(coll_ref, 50)
	# Check header
	header = next(lines)
	required_fields = {'location', 'machine_id', 'description'}
	if not set(required_fields).issubset(header):
		raise Exception('Missing required header field(s)', 400)

	locationIndex = header.index('location')
	machineIdIndex = header.index('machine_id')
	descriptionIndex = header.index('description')

	for line in lines:

		if len(line) == 0:
			break

		location = line[locationIndex]
		machine_id = line[machineIdIndex]
		description = line[descriptionIndex]
		if 'progressive_count' in header:
			contents = line[header.index('progressive_count')].strip()
			progressive_count = contents if len(contents) > 0 else None
		else:
			progressive_count = None

		if 'user' in header:
			contents = line[header.index('user')].strip()
			user = contents if len(contents) > 0 else None
		else:
			user = None

		p_1 = p_2 = p_3 = p_4 = p_5 = p_6 = p_7 = p_8 = p_9 = p_10 = None

		if ('p_1' in header):
			p_1 = line[header.index('p_1')].strip()
			p_1 = p_1 if len(p_1) > 0 else None

		if ('p_2' in header):
			p_2 = line[header.index('p_2')].strip()
			p_2 = p_2 if len(p_2) > 0 else None

		if ('p_3' in header):
			p_3 = line[header.index('p_3')].strip()
			p_3 = p_3 if len(p_3) > 0 else None

		if ('p_4' in header):
			p_4 = line[header.index('p_4')].strip()
			p_4 = p_4 if len(p_4) > 0 else None

		if ('p_5' in header):
			p_5 = line[header.index('p_5')].strip()
			p_5 = p_5 if len(p_5) > 0 else None

		if ('p_6' in header):
			p_6 = line[header.index('p_6')].strip()
			p_6 = p_6 if len(p_6) > 0 else None

		if ('p_7' in header):
			p_7 = line[header.index('p_7')].strip()
			p_7 = p_7 if len(p_7) > 0 else None

		if ('p_8' in header):
			p_8 = line[header.index('p_8')].strip()
			p_8 = p_8 if len(p_8) > 0 else None

		if ('p_9' in header):
			p_9 = line[header.index('p_9')].strip()
			p_9 = p_9 if len(p_9) > 0 else None

		if ('p_10' in header):
			p_10 = line[header.index('p_10')].strip()
			p_10 = p_10 if len(p_10) > 0 else None

		progressive_titles = [p_1, p_2, p_3, p_4, p_5, p_6, p_7, p_8, p_9, p_10]

		_insert_to_database(uid, location, machine_id, description, progressive_count, user, progressive_titles)

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










