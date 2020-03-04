## Meter Image Capturing Flask Web Portal ##

To check if dependencies are up to date: 
```
// Ensure the virtual environment is activated:
source env/bin/activate
// List outdated pip dependencies
pip3 list --outdated
// Upgrade any out of date dependencies
pip3 install --upgrade <dependency_name>
// Finally, update requirements.txt
pip3 freeze > requirements.txt
```

To run in a development environment (remain in virtual env like above): 

First set google cloud services environment variables in bash:
```
export GOOGLE_APPLICATION_CREDENTIALS="serviceAccountKey.json"
```

Then run the following in the Python shell:
```
python3 app.py
```

To run in a production environment on Heroku:
```
gunicorn wsgi:app
```