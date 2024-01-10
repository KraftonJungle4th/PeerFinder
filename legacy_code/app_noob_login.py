#################################################
# 기초적인 로그인 구현 후 JWT 구현, 기존 로그인 코드
#################################################

# from bson import ObjectId
# from pymongo import MongoClient
# from flask import Flask,request,jsonify,render_template,redirect,url_for,flash
# from flask.json.provider import JSONProvider

# import json
# import sys
# import os

            
# # flask객체 생성
# app = Flask(__name__)
# app.secret_key = "My_Key"


# # EC2용 코드
# # client = MongoClient("mongodb://test:test@localhost", 27017)


# bcrypt = Bcrypt(app)
# # JWT 매니저 활성화
# jwt = JWTManager(app)
# # localhost용 코드
# client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
# db = client.dbjungle  # 'dbjungle'라는 이름의 db를 만듭니다.

# ####################################################################################
# # 이 부분은 코드를 건드리지 말고 그냥 두세요. 코드를 이해하지 못해도 상관없는 부분입니다.

# # ObjectId 타입으로 되어있는 _id 필드는 Flask 의 jsonify 호출시 문제가 된다.
# # 이를 처리하기 위해서 기본 JsonEncoder 가 아닌 custom encoder 를 사용한다.
# # Custom encoder 는 다른 부분은 모두 기본 encoder 에 동작을 위임하고 ObjectId 타입만 직접 처리한다.
# class CustomJSONEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, ObjectId):
#             return str(o)
#         return json.JSONEncoder.default(self, o)


# class CustomJSONProvider(JSONProvider):
#     def dumps(self, obj, **kwargs):
#         return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

#     def loads(self, s, **kwargs):
#         return json.loads(s, **kwargs)


# # 위에 정의되 custom encoder 를 사용하게끔 설정한다.
# app.json = CustomJSONProvider(app)

# # 여기까지 이해 못해도 그냥 넘어갈 코드입니다.
# #####################################################################################

# # Pages
# #############################################
# @app.route("/", methods=["GET"])
# def get_home():
#     return render_template("index.html")

# @app.route("/signup", methods=["GET"])
# def getSignUp():
#     return render_template("auth/signup.html")

# ##############################################

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


# if __name__ == "__main__":
#     print(sys.executable)
#     app.run("0.0.0.0", port=5000, debug=True)