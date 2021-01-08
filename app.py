#
# To run:
# source env/bin/activate (if using local virtual environment)
# python3 app.py
# 

from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

DEBUG = False

@app.route('/')
def index():
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


if __name__ == '__main__':
	
	HOST = '127.0.0.1'
	PORT = 5000
	app.run(host=HOST, port=PORT, debug=DEBUG)










