from base64 import encode

import bcrypt
def hash_pswd(raw_password: str) -> str:
    salt = b'$2b$12$qYK7R5dqRIvSIAq40fcXte' # 这个是之前生成的一个salt，检测密码是否正确的逻辑就是把用户输入的密码用这个salt再加密一次
    #byte_password = encode(raw_password, 'utf-8') # 原始密码转字节字符串
    byte_password = raw_password.encode('utf-8')
    hashed_password = bcrypt.hashpw(byte_password,salt) #字节字符串生成hash
    normalized_password = hashed_password.decode('utf-8')
    return normalized_password

def verify(input,hashed_password):

    salt = b'$2b$12$qYK7R5dqRIvSIAq40fcXte' # 上面的盐
    input_hased=input.encode('utf-8') # 用户输入密码转字节字符串
    hashed_input=bcrypt.hashpw(input_hased,salt) #处理后的用户输入密码生成hash

    #根据函数的返回值来定义用户的登录状态
    if hashed_input==hashed_password:
        return True
    else:
        return False

