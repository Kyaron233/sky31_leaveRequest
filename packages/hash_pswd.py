

import bcrypt
#def hash_pswd_old(raw_password: str) -> str:
   #salt = bcrypt.gensalt()
    #byte_password = encode(raw_password, 'utf-8') # 原始密码转字节字符串
    #byte_password = raw_password.encode('utf-8')
    #hashed_password = bcrypt.hashpw(byte_password,salt) #字节字符串生成hash
    #normalized_password = hashed_password.decode('utf-8')
    #return normalized_password

def isPswdCorrect(input,hashed_password):
    input = input.encode('utf-8')
    hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(input,hashed_password)

def hash_pswd(raw_password: str) :
    salt = bcrypt.gensalt() # 随机生成salt
    byte_password = raw_password.encode('utf-8') # 转换成字节字符串
    hashed_password = bcrypt.hashpw(byte_password,salt) # 生成hash
    hashed_password_str = hashed_password.decode('utf-8')
    return hashed_password_str # 返回值应修改成普通字符串


