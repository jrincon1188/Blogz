import hashlib

def make_pwd_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()    

def check_pwd_hash(pasword, hash):    
    if make_pwd_hash(password) == hash:
        return True
    return False