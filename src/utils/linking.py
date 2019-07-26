import hashlib

def hash_email(email):
    return hashlib.md5(email.encode()).hexdigest()