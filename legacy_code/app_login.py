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


# API #1: HTML 틀(template) 전달
# 틀 안에 데이터를 채워 넣어야 하는데 이는 아래 이어지는 /api/list 를 통해 이루어집니다.

# # API #2: 로그인
# @app.route("/", methods=["POST"])
# def Login():
#     UserId = request.form.get("_email")
#     UserPw = request.form.get("_password")
#     # 1. 아이디와 비밀번호가 유저중에 있는지
#     ID = FindEmail(UserId)
#     error = None
#     if ID == None:
#         flash("중복된 이메일 주소입니다.","info")
#         error = 1
#         return render_template("index.html",error=error)
#     elif (ID['Password']==UserPw):
#         return redirect(url_for("getSignUp"))
#     else:
#         flash("비밀번호가 일치하지 않습니다","info")
#         error = 2
#         return render_template("index.html",error=error)

# def FindEmail(email):
#     return db.Users.find_one({"ID":email})


# # API #3: 회원가입
# @app.route("/SignUp", methods=["POST"])
# def signUp():

#     UserId = request.form.get("_email")
#     UserPw = request.form.get("_password")
#     # 1. 아이디가 동일한 유저가 있는지 미구현
#     # ID = FindEmail(UserId)
#     # if ID['ID']==UserId :
#     #     return jsonify({"result": "failure"})
#     # else :
#     #     doc = {
#     #         "ID": UserId,
#     #         "Password": UserPw,
#     #         "Name": None,
#     #         "Ages": None,
#     #         "MajorStatus": None,
#     #         "Stack": None,
#     #         "FreeWord": None,
#     #         "likes": False,
#     #         "ProfileEdit": False,
#     #     }
#     #     db.Users.insert_one(doc)
#     #     return redirect(url_for("home"))
#     doc = {
#             "ID": UserId,
#             "Password": UserPw,
#             "Name": None,
#             "Ages": None,
#             "MajorStatus": None,
#             "Stack": None,
#             "FreeWord": None,
#             "likes": False,
#             "ProfileEdit": False,
#         }
#     db.Users.insert_one(doc)
#     return redirect(url_for("home"))
    


# def show_movies():
#     # client 에서 요청한 정렬 방식이 있는지를 확인합니다. 없다면 기본으로 좋아요 순으로 정렬합니다.
#     sortMode = request.args.get("sortMode", "likes")
#     trashMode = request.args.get("trashMode", "false")
    
#     trashMode = True if trashMode == "true" else False

#     # 1. db에서 trashed 가 False인 movies 목록을 검색합니다. 주어진 정렬 방식으로 정렬합니다.
#     # 참고) find({},{}), sort()를 활용하면 됨.
#     # 개봉일 순서 정렬처럼 여러 기준으로 순서대로 정렬해야되는 경우 sort([('A', 1), ('B', 1)]) 처럼 줄 수 있음.
#     if sortMode == "likes":
#         movies = list(db.movies.find({"trashed": trashMode}).sort("likes", -1))
#     elif sortMode == "viewers":
#         movies = list(db.movies.find({"trashed": trashMode}).sort("viewers", -1))
#     elif sortMode == "date":
#         movies = list(
#             db.movies.find({"trashed": trashMode}).sort(
#                 [("open_year", -1), ("open_month", -1), ("open_day", -1)]
#             )
#         )
#     else:
#         return jsonify({"result": "failure"})
    
#     if (movies == None):
#         return jsonify({"result": "failure"})

#     # 2. 성공하면 success 메시지와 함께 movies_list 목록을 클라이언트에 전달합니다.
#     return jsonify({"result": "success", "movies_list": movies})




# # API #3: 영화에 좋아요 숫자를 하나 올립니다.
# @app.route("/api/movie/like", methods=["POST"])
# def like_movie():
#     movie_id = request.form["_id"]

#     # 1. movies 목록에서 find_one으로 영화 하나를 찾습니다.
#     movie = find_movie(movie_id)

#     if movie == None:
#         return jsonify({"result": "failure"})

#     # 2. movie의 like 에 1을 더해준 new_like 변수를 만듭니다.
#     new_likes = movie["likes"] + 1

#     # 3. movies 목록에서 id 가 매칭되는 영화의 like 를 new_like로 변경합니다.
#     # 참고: '$set' 활용하기!
#     result = db.movies.update_one(
#         {"_id": ObjectId(movie_id)}, {"$set": {"likes": new_likes}}
#     )

#     # 4. 하나의 영화만 영향을 받아야 하므로 result.updated_count 가 1이면 result = success 를 보냄
#     if result.modified_count == 1:
#         return jsonify({"result": "success"})
#     else:
#         return jsonify({"result": "failure"})


# @app.route("/api/movie/controlTrash", methods=["POST"])
# def control_trash_movie():
#     movie_id = request.form["_id"]
#     movie_trashed = request.form["trashed"]

#     # 1. movies 목록에서 find_one으로 영화 하나를 찾습니다.
#     movie = find_movie(movie_id)
#     result = None

#     if movie == None:
#         return jsonify({"result": "failure"})

#     if movie_trashed == "false":  # trashMovie
#         # 2-1. 버려지지 않은 영화라면 movie의 trashed 를 True 로 변경합니다.
#         if movie["trashed"] == False:
#             result = db.movies.update_one(
#                 {"_id": ObjectId(movie_id)}, {"$set": {"trashed": True}}
#             )

#             if result == None:
#                 return jsonify({"result": "failure"})
#     elif movie_trashed == "true":  # restoreMovie
#         # 2-2. 버려진 영화라면 movie의 trashed 를 False 로 변경합니다.
#         if movie["trashed"] == True:
#             result = db.movies.update_one(
#                 {"_id": ObjectId(movie_id)}, {"$set": {"trashed": False}}
#             )

#             if result == None:
#                 return jsonify({"result": "failure"})

#     # 3. 하나의 영화만 영향을 받아야 하므로 result.updated_count 가 1일 때만 result = success 를 보냅니다.
#     if result.modified_count == 1:
#         return jsonify({"result": "success"})
#     else:
#         return jsonify({"result": "failure"})


# @app.route("/api/movie/delete", methods=["POST"])
# def delete_movie():
#     movie_id = request.form["_id"]

#     # 1. movies 목록에서 find_one으로 영화 하나를 찾습니다.
#     movie = find_movie(movie_id)

#     if movie == None:
#         return jsonify({"result": "failure"})

#     # 2. 영화를 완전히 삭제합니다.
#     if movie["trashed"] == True:
#         result = db.movies.delete_one({"_id": ObjectId(movie_id)})

#         if result == None:
#             return jsonify({"result": "failure"})

#     # 3. 하나의 영화만 영향을 받아야 하므로 result.deleted_count 가 1일 때만 result = success 를 보냅니다.
#     if result.deleted_count == 1:
#         return jsonify({"result": "success"})
#     else:
#         return jsonify({"result": "failure"})


if __name__ == "__main__":
    print(sys.executable)
    app.run("0.0.0.0", port=5000, debug=True)
