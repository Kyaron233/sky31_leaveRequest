import bcrypt

def hash_password(password):

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed

def verify_password(input_password, stored_password):

    return bcrypt.checkpw(input_password.encode('utf-8'), stored_password)
