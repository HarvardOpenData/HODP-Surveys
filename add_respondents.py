import csv
import sys
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime

if len(sys.argv) < 2:
    print("Import csv required")
    exit(0)

if len(sys.argv) < 3:
    print("Column indices required")
    exit(0)

file_name = sys.argv[1]
email_col = int(sys.argv[2]) - 1
emails = []
with open(file_name) as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        if len(sys.argv) > 3:
            col = int(sys.argv[3]) - 1
            if("yes" in row[col].lower()):
                emails.append(row[email_col])
        else:
            emails.append(row[email_col])


cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': "hodp-surveys",
})

db = firestore.client()

emails_ref = db.collection(u"emails")

for email in emails:
    email = email.lower()
    docs = emails_ref.where(u"email", "==", email).get()
    isEmpty = True
    for doc in docs:
        isEmpty = False
        break
    if isEmpty:
        emails_ref.add({"email" : email, "last_contact" : datetime.datetime.min})