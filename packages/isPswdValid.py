# 密码要求如下
#1.长度为8-16个字符
#2.必须包含字母和数字，字母不限制大小写，可使用英文符号
#3.其他的输入（中文汉字，中文符号等）不被接受

import re

def is_valid_pswd(s: str) -> bool:
    # 检查长度是否在8-16之间
    if not (8 <= len(s) <= 16):
        return False

    # 检查是否包含至少一个字母和一个数字
    if not (re.search(r'[A-Za-z]', s) and re.search(r'\d', s)):
        return False

    # 检查是否只包含字母、数字和英文符号
    if not re.fullmatch(r'[A-Za-z0-9!@#$%^&*()_+\-={}\[\]:;"\'<>?,./`~\\]*', s):
        return False

    return True
