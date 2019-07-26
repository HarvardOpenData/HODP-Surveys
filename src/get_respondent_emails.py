from utils import firebasedb, linking
import csv
import sys

def main():
    output_filename = sys.argv[1] if len(sys.argv) > 1 else "active_resondents.csv"

    firebasedb.init_survey_firebase()
    db = firebasedb.get_survey_firestore_client()
    respondents = get_active_respondents(db)

    with open("active_respondents.csv", "w+") as output_file:
        fieldnames = ["email", "year"]
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for respondent in respondents:
            writer.writerow(respondent)
        

def get_active_respondents(db): 
    emails_ref = db.collection("emails")
    responses_ref = db.collection("responses")

    email_docs = emails_ref.where("has_demographics", "==", True).stream()

    respondents = []

    for doc in email_docs:
        doc_id = doc.id
        responses_doc = responses_ref.document(linking.hash_email(doc_id)).get()
        responses_dict = responses_doc.to_dict() 
        year = responses_dict["demographics"]["year"]
        respondent = { 
            "email" : doc_id,
            "year" : year
        }
        respondents.append(respondent)
    return respondents


    

if __name__ == "__main__":
    main()

