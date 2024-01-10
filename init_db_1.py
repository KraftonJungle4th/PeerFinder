import random
import requests
from flask_bcrypt import Bcrypt,generate_password_hash
from bs4 import BeautifulSoup
from pymongo import MongoClient  

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbjungle  # 'dbjungle'라는 이름의 db를 만듭니다.


def InsertUser():
    
    user_pw = '1234'
    pw_hash = generate_password_hash(user_pw,10)
    doc = {
        "user_id": 'test@test.com',
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
    print(
        "완료",
    )


if __name__ == "__main__":
    # 기존의 Users db 삭제하기
    db.Users.drop()

    # default Users 넣기
    InsertUser()