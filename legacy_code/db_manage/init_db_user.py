from pymongo import MongoClient
from flask_bcrypt import generate_password_hash

import config

client = MongoClient(config.MONGO_DB_URI)
db = client.dbjungle


def InsertUser():
    user_id = ("test@test.com",)
    user_pw = "1234"
    pw_hash = generate_password_hash(user_pw, 10)
    doc = {
        "user_id": user_id,
        "user_pw": pw_hash,
        "Name": None,
        "Ages": None,
        "MajorStatus": None,
        "Stack": None,
        "FreeWord": None,
        "likes": False,
        "ProfileEdit": False,
    }

    db.Users.insert_one(doc)
    
    print("완료: ", user_id, pw_hash)

if __name__ == "__main__":
    # 기존의 Users db 삭제하기
    db.Users.drop()

    # default Users 넣기
    InsertUser()
