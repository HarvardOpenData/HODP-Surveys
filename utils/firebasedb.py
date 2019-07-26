import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

def init_survey_firebase():
    # we're on the server, use the project ID
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'projectId': "hodp-surveys",
        }, name="surveys")
    # locally testing, we have some credential file
    else:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'survey_creds.json'
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, name="surveys")

def get_survey_firestore_client():
    app = firebase_admin.get_app("surveys")
    return firestore.client(app)