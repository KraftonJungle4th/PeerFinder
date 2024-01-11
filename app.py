import json
import sys

from bson import ObjectId
from pymongo import MongoClient
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    JWTManager,
    get_jwt,
    create_refresh_token,
    set_access_cookies,
)
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from flask.json.provider import JSONProvider


# flask 객체 생성
app = Flask(__name__)
app.config.from_object("config")

app.secret_key = "My_Key"

app.config["JWT_COOKIE_SECURE"] = app.config["PEERFINDER_JWT_COOKIE_SECURE"]
app.config["JWT_TOKEN_LOCATION"] = app.config["PEERFINDER_JWT_TOKEN_LOCATION"]
app.config["JWT_SECRET_KEY"] = app.config["PEERFINDER_JWT_SECRET_KEY"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = app.config[
    "PEERFINDER_JWT_ACCESS_TOKEN_EXPIRES"
]

bcrypt = Bcrypt(app)

# JWT 매니저 활성화
jwt = JWTManager(app)

# localhost용 코드
client = MongoClient(app.config["MONGO_DB_URI"])
db = client.get_default_database()


#####################################################################################
# ObjectId 타입으로 되어있는 _id 필드는 Flask 의 jsonify 호출시 문제가 된다.
# 이를 처리하기 위해서 기본 JsonEncoder 가 아닌 custom encoder 를 사용.
# Custom encoder는 ObjectId 타입만 직접 처리하고 다른 부분은 모두 기본 encoder에 동작 위임
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)


# 위에 정의된 custom encoder 를 사용하게끔 설정
app.json = CustomJSONProvider(app)
# #####################################################################################


# Pages
##############################################
@app.route("/", methods=["GET"])
def get_home():
    return render_template("index.html")


@app.route("/signup", methods=["GET"])
def getSignUp():
    return render_template("pages/signup.html")

@app.route("/profile", methods=["GET"])
def getprofile():
    return render_template("pages/profile.html")

@app.route("/myprofile", methods=["GET"])
def getmyprofile():
    return render_template("pages/myprofile.html")


###############################################


# JWT 가입
@app.route("/signup", methods=["POST"])
def signup():
    # id, password 받아오고 저장
    user_id = request.form["user_id"]
    user_pw = request.form["user_pw"]
    pw_hash = generate_password_hash(user_pw, 10)

    # id 중복확인
    if db.Users.count_documents({"user_id": user_id}) == 0:
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

        flash("회원가입 성공!")
        return redirect(url_for("get_home"))
    else:
        flash("이미 존재하는 아이디 입니다.")
        return redirect(url_for("getSignUp"))


# 로그인 api
@app.route("/", methods=["POST"])
def user_login():
    user_id = request.form["user_id"]
    user_pw = request.form["user_pw"]

    if db.Users.count_documents({"user_id": user_id}) == 0:  # id 확인
        # 401 error : 인증 자격 없음
        return jsonify({"result": "fail", "message": "아이디가 틀립니다."})  # 401
    else:  # 비번 확인
        check_pw = db.Users.find_one({"user_id": user_id})
        if check_password_hash(check_pw.get("user_pw"), user_pw):
            response = jsonify({"result": "success", "message": "로그인 성공"})
            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)
            # session['logged_in'] = True
            set_access_cookies(response, access_token)
            return redirect(url_for("getprofile"))
        else:
            return jsonify({"result": "fail", "message": "틀린 비밀번호입니다."})



# 로그인 필요한 api 접근
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # 로그인 상태 확인 후 user identity 정보 return
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


# blocklist 생성
jwt_blocklist = set()


# blocklist 기능사용
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in jwt_blocklist


# 로그아웃 처리 api
@app.route("/logout", methods=["GET"])
@jwt_required()
def user_logout():
    jti = get_jwt()["jti"]
    jwt_blocklist.add(jti)


@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))

        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity)
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response


if __name__ == "__main__":
    print(sys.executable)
    app.run("0.0.0.0", port=5000, debug=True)
