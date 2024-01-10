import random
import requests
from flask_bcrypt import Bcrypt,generate_password_hash
from bs4 import BeautifulSoup
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbjungle  # 'dbjungle'라는 이름의 db를 만듭니다.


def InsertUser():
    # URL을 읽어서 HTML를 받아오고,
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
    }
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
    # 기존의 movies 콜렉션을 삭제하기
    db.Users.drop()

    # 영화 사이트를 scraping 해서 db 에 채우기
    InsertUser()