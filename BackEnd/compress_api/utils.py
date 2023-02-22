import bcrypt
import re
import base64

class passwd():
    def hash_passwd(passwd):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(passwd, salt)
        return hashed

    def check_passwd(passwd, hashed):
        if bcrypt.checkpw(passwd, hashed):
            return True
        else:
            return False
    def complex_passwd(passwd):
        passwd_len = True if  len(passwd) > 8 else False
        passwd_num = re.search(r"\d", passwd) is not None
        passwd_upp = re.search(r"[A-Z]", passwd) is not None
        passwd_low = re.search(r"[a-z]", passwd) is not None
        passwd_esp = re.search(r"\W", passwd) is not None

        response = {
            'len': passwd_len,
            'num': passwd_num,
            'upp': passwd_upp,
            'low': passwd_low,
            'esp': passwd_esp
        }

        return response

class file2base():
    def base64file(path):
        with open(path, "rb") as f:
            encoded_string = base64.b64encode(f.read())
        return encoded_string
