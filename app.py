import json
import sys

from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider

app = Flask(__name__)
app.config.from_object("config")

client = MongoClient(app.config["MONGO_DB_URI"])
db = client.get_default_database()

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

app.json = CustomJSONProvider(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/movie/list", methods=["GET"])
def show_movies():
    sortMode = request.args.get("sortMode", "likes")
    trashMode = request.args.get("trashMode", "false")

    trashMode = True if trashMode == "true" else False

    # 참고) find({},{}), sort()를 활용하면 됨.
    # 개봉일 순서 정렬처럼 여러 기준으로 순서대로 정렬해야되는 경우 sort([('A', 1), ('B', 1)]) 처럼 줄 수 있음.
    if sortMode == "likes":
        movies = list(db.movies.find({"trashed": trashMode}).sort("likes", -1))
    elif sortMode == "viewers":
        movies = list(db.movies.find({"trashed": trashMode}).sort("viewers", -1))
    elif sortMode == "date":
        movies = list(
            db.movies.find({"trashed": trashMode}).sort(
                [("open_year", -1), ("open_month", -1), ("open_day", -1)]
            )
        )
    else:
        return jsonify({"result": "failure"})

    if movies == None:
        return jsonify({"result": "failure"})

    return jsonify({"result": "success", "movies_list": movies})

def find_movie(movie_id):
    return db.movies.find_one({"_id": ObjectId(movie_id)})

# API #3: 영화에 좋아요 숫자를 하나 올립니다.
@app.route("/api/movie/like", methods=["POST"])
def like_movie():
    movie_id = request.form["_id"]

    # 1. movies 목록에서 find_one으로 영화 하나를 찾습니다.
    movie = find_movie(movie_id)

    if movie == None:
        return jsonify({"result": "failure"})

    # 2. movie의 like 에 1을 더해준 new_like 변수를 만듭니다.
    new_likes = movie["likes"] + 1

    # 3. movies 목록에서 id 가 매칭되는 영화의 like 를 new_like로 변경합니다.
    # 참고: '$set' 활용하기!
    result = db.movies.update_one(
        {"_id": ObjectId(movie_id)}, {"$set": {"likes": new_likes}}
    )

    # 4. 하나의 영화만 영향을 받아야 하므로 result.updated_count 가 1이면 result = success 를 보냄
    if result.modified_count == 1:
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "failure"})


@app.route("/api/movie/controlTrash", methods=["POST"])
def control_trash_movie():
    movie_id = request.form["_id"]
    movie_trashed = request.form["trashed"]

    # 1. movies 목록에서 find_one으로 영화 하나를 찾습니다.
    movie = find_movie(movie_id)
    result = None

    if movie == None:
        return jsonify({"result": "failure"})

    if movie_trashed == "false":  # trashMovie
        # 2-1. 버려지지 않은 영화라면 movie의 trashed 를 True 로 변경합니다.
        if movie["trashed"] == False:
            result = db.movies.update_one(
                {"_id": ObjectId(movie_id)}, {"$set": {"trashed": True}}
            )

            if result == None:
                return jsonify({"result": "failure"})
    elif movie_trashed == "true":  # restoreMovie
        # 2-2. 버려진 영화라면 movie의 trashed 를 False 로 변경합니다.
        if movie["trashed"] == True:
            result = db.movies.update_one(
                {"_id": ObjectId(movie_id)}, {"$set": {"trashed": False}}
            )

            if result == None:
                return jsonify({"result": "failure"})

    # 3. 하나의 영화만 영향을 받아야 하므로 result.updated_count 가 1일 때만 result = success 를 보냅니다.
    if result.modified_count == 1:
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "failure"})


@app.route("/api/movie/delete", methods=["POST"])
def delete_movie():
    movie_id = request.form["_id"]

    # 1. movies 목록에서 find_one으로 영화 하나를 찾습니다.
    movie = find_movie(movie_id)

    if movie == None:
        return jsonify({"result": "failure"})

    # 2. 영화를 완전히 삭제합니다.
    if movie["trashed"] == True:
        result = db.movies.delete_one({"_id": ObjectId(movie_id)})

        if result == None:
            return jsonify({"result": "failure"})

    # 3. 하나의 영화만 영향을 받아야 하므로 result.deleted_count 가 1일 때만 result = success 를 보냅니다.
    if result.deleted_count == 1:
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "failure"})


if __name__ == "__main__":
    print(sys.executable)
    app.run("0.0.0.0", port=5000, debug=True)