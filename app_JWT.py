from bson import ObjectId
from pymongo import MongoClient
from flask_jwt_extended import create_access_token,get_jwt_identity,jwt_required,JWTManager,get_jwt, create_refresh_token,set_access_cookies
from flask import Flask,request,jsonify,render_template,redirect,url_for,flash
from flask_bcrypt import Bcrypt,generate_password_hash,check_password_hash
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from flask.json.provider import JSONProvider

import json
import sys
import os

            
# flask객체 생성
app = Flask(__name__)
app.secret_key = "My_Key"

app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_SECRET_KEY"] = "hyuk-is-coding..."
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

app.config.update(
    DEBUG=True,
    JWT_SECRET_KEY = "JUNGLEPROFILES",
)


# EC2용 코드
# client = MongoClient("mongodb://test:test@localhost", 27017)


bcrypt = Bcrypt(app)
# JWT 매니저 활성화
jwt = JWTManager(app)
# localhost용 코드
client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbjungle  # 'dbjungle'라는 이름의 db를 만듭니다.

#####################################################################################
# 이 부분은 코드를 건드리지 말고 그냥 두세요. 코드를 이해하지 못해도 상관없는 부분입니다.
#
# ObjectId 타입으로 되어있는 _id 필드는 Flask 의 jsonify 호출시 문제가 된다.
# 이를 처리하기 위해서 기본 JsonEncoder 가 아닌 custom encoder 를 사용한다.
# Custom encoder 는 다른 부분은 모두 기본 encoder 에 동작을 위임하고 ObjectId 타입만 직접 처리한다.
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


# 위에 정의되 custom encoder 를 사용하게끔 설정한다.
app.json = CustomJSONProvider(app)

# 여기까지 이해 못해도 그냥 넘어갈 코드입니다.
# #####################################################################################

# Pages
##############################################
@app.route("/", methods=["GET"])
def get_home():
    return render_template("index.html")

@app.route("/signup", methods=["GET"])
def getSignUp():
    return render_template("auth/signup.html")

###############################################

# JWT
# 가입
@app.route('/signup', methods=['POST'])
def signup():
    #id, password 받아오고 저장
    user_id = request.form['user_id']
    user_pw = request.form['user_pw']
    pw_hash = generate_password_hash(user_pw,10)
    #id 중복확인
    if db.Users.count_documents({'user_id': user_id}) == 0 :
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
        # return redirect(url_for("get_home"))
        flash("회원가입 성공!")
        return redirect(url_for("get_home"))
        return jsonify({'result':'success','meassage':'회원가입 성공'})
    else:
        # return redirect(url_for("getSignUp"))
        flash("이미 존재하는 아이디 입니다.")
        return redirect(url_for("getSignUp"))
        return jsonify({'result':'fail','messsage':'아이디가 이미 존재합니다.'})


# 로그인 api
@app.route('/', methods=['POST'])
def user_login() :

    user_id = request.form['user_id']
    user_pw = request.form['user_pw']
    
    # id 확인
    if db.Users.count_documents({'user_id':user_id}) == 0:
        # 401 error : 인증 자격 없음
        return jsonify({'result':'fail','message':'아이디가 틀립니다.'}) #, 401
    # 비번 확인
    else:
        check_pw = db.Users.find_one({'user_id':user_id})
        if check_password_hash(check_pw.get('user_pw'),user_pw):
            response = jsonify({'result':'success','message':'로그인 성공'})
            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)
            # session['logged_in'] = True
            set_access_cookies(response,access_token)
            return response
        else:
            return jsonify({'result': 'fail','message':'틀린 비밀번호입니다.'})
        

    
    return jsonify(access_token=access_token)

#로그인 필요한 api 접근
@app.route('/protected',methods=['GET'])
@jwt_required()
def protected():
    #로그인 상태 확인 후 user identity 정보 return
    current_user = get_jwt_identity()
    return jsonify(logged_in_as = current_user), 200

# blocklist 생성
jwt_blocklist = set()

#blocklist 기능사용
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header,jwt_payload) :
    jti = jwt_payload['jti']
    return jti in jwt_blocklist

#로그아웃 처리 api
@app.route('/logout', methods=['GET'])
@jwt_required()
def user_logout() :
    jti = get_jwt()['jti']
    jwt_blocklist.add(jti)

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()['exp']
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity)
            set_access_cookies = (response,access_token)
        return response
    except(RuntimeError,KeyError):
        return response
    

if __name__ == "__main__":
    print(sys.executable)
    app.run("0.0.0.0", port=5000, debug=True)
