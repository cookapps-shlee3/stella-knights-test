import time
import jwt


key = "Cook!234"
    
def get(data, expired = 86400*30):
    data['iat'] = int(time.time())
    data['nbf'] = int(time.time())
    data['exp'] = int(time.time() + expired)
    encoded = jwt.encode(data, key, algorithm="HS256")
    return encoded


def parse(token):
    decoded = jwt.decode(token, key, algorithms="HS256")
    return decoded


if __name__ == "__main__":
    print(get({'uid':10006}))