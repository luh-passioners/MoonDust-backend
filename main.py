from flask import Flask, jsonify, request
from flask_cors import CORS
from db import get_collection
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from bson.objectid import ObjectId
import keys

app = Flask(__name__)

# JWT
app.config["JWT_SECRET_KEY"] = keys.JWT_SECRET_KEY  # Change this!
jwt = JWTManager(app)

# CORS
CORS(app)

API_PREFIX = "/api/v1"
def r(endpoint):
  return f"{API_PREFIX}{endpoint}"


# POST: signup
@app.route(r("/signup"), methods=["POST"])
def signup():
  username = request.json.get("username")
  password = request.json.get("password")

  hashed = keys.hash(password)

  user_data = {
    "username": username,
    "name": request.json.get("name"),
    "hashed": hashed,
    "company": request.json.get("company"), # company name
    "type": request.json.get("type"), # "full" | "org"
  }

  if user_data == "org":
    user_data["org_id"] = ObjectId(request.json.get("org_id"))

  res = get_collection("users").insert_one(user_data)

  id = str(res.inserted_id)
  access_token = create_access_token(id)

  return jsonify({
    "token": access_token
  })

# POST: login
@app.route(r("/login"), methods=["POST"])
def login():
  username = request.json.get("username")
  password = request.json.get("password")

  match_cursor = get_collection("users").find({ "username": username })

  match_list = [match for match in match_cursor]

  if len(match_list) != 1:
    return jsonify({
      "success": False,
    })
  
  match = match_list[0]

  if keys.hash(password) == match["hashed"]:
    access_token = create_access_token(str(match["_id"]))

    return jsonify({
      "success": True,
      "token": access_token
    })
  
  return jsonify({
    "success": False,
  })

# GET: all transactions
@app.route(r("/transactions"), methods=["GET"])
@jwt_required()
def get_transactions():
  current_user = ObjectId(get_jwt_identity())

  match_cursor = get_collection("users").find({ "_id": current_user })
  match_list = [match for match in match_cursor]
  if len(match_list) != 1: # fake jwt
    return jsonify({
      "success": False,
    })
  user = match_list[0]
  trans = get_collection("transactions").find({ "company": user["company"] })
  
  jsonable_trans = [{
    "_id": str(item["_id"]),
    "name": item["name"],
    "company": item["company"],
    "org_id": item["org_id"],
    "date": item["date"],
    "amount": item["amount"]
  } for item in trans]

  return jsonify(jsonable_trans)

# POST: add a transaction
@app.route(r("/transactions"), methods=["POST"])
@jwt_required()
def add_transaction():
  current_user = ObjectId(get_jwt_identity())
  
  match_cursor = get_collection("users").find({ "_id": current_user })
  match_list = [match for match in match_cursor]
  if len(match_list) != 1:
    return jsonify({
      "success": False,
    })
  user = match_list[0]

  new_trans = {
    "name": request.json.get("name"),
    "company": user["company"],
    "org_id": ObjectId(request.json.get("org_id")),
    "date": request.json.get("date"),
    "amount": request.json.get("amount"),
  }

  return jsonify({
    "_id": str(get_collection("transactions").insert_one(new_trans).inserted_id)
  })

# GET: all orgs
@app.route(r("/orgs"), methods=["GET"])
@jwt_required()
def get_orgs():
  current_user = ObjectId(get_jwt_identity())

  match_cursor = get_collection("users").find({ "_id": current_user })
  match_list = [match for match in match_cursor]
  if len(match_list) != 1: # fake jwt
    return jsonify({
      "success": False,
      "meow": current_user
    })
  user = match_list[0]

  company = user["company"]
  orgs = get_collection("orgs")
  orgs_cursor = orgs.find({ "company": company })
  org_map = {}

  for org in orgs_cursor:
    org_map[str(org["id"])] = org["name"]

  return jsonify({
    "success": True,
    "org_map": org_map
  })

# POST: create org
@app.route(r("/orgs"), methods=["POST"])
@jwt_required()
def add_org():
  current_user = ObjectId(get_jwt_identity())

  match_cursor = get_collection("users").find({ "_id": current_user })
  match_list = [match for match in match_cursor]
  if len(match_list) != 1: # fake jwt
    return jsonify({
      "success": False,
      "meow": current_user
    })
  user = match_list[0]

  if user["type"] != "full": # access level too little
    return jsonify({
      "success": False
    })

  res = get_collection("orgs").insert_one({
    "company": user["company"],
    "name": request.json.get("name")
  })

  return jsonify({
    "success": True,
    "_id": str(res.inserted_id)
  })

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)