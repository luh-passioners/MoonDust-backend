from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from bson.objectid import ObjectId

from db import get_collection
import keys
import utils

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
  try:
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

    get_collection("users").insert_one(user_data)
    user_data["_id"] = str(user_data["_id"])
    access_token = create_access_token(user_data["_id"])

    if "org_id" in user_data:
      user_data["org_id"] = str(user_data["org_id"])

    return jsonify({
      "success": True,
      "token": access_token,
      "user": user_data
    }), 201
  except Exception as ex:
    
    return jsonify({
      "success": False,
      "error": str(ex),
    }), 500

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
    }), 403
  
  match = match_list[0]
  match["_id"] = str(match["_id"])

  if keys.hash(password) == match["hashed"]:
    access_token = create_access_token(match["_id"])

    return jsonify({
      "success": True,
      "token": access_token,
      "user": match
    }), 201
  
  return jsonify({
    "success": False,
  }), 500

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
    }), 403
  user = match_list[0]
  trans = get_collection("transactions").find({ "company": user["company"] })
  
  jsonable_trans = [{
    "_id": str(item["_id"]),
    "name": item["name"],
    "company": item["company"],
    "org_id": str(item["org_id"]),
    "date": item["date"],
    "amount": item["amount"]
  } for item in trans]

  if user["type"] == "org":
    jsonable_trans = filter(lambda tr: tr["org_id"] == str(user["org_id"]), jsonable_trans)

  print(jsonable_trans)

  return jsonify({ "success": True, "transactions": jsonable_trans }), 200

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
    }), 403
  user = match_list[0]

  new_trans = {
    "name": request.json.get("name"),
    "company": user["company"],
    "org_id": ObjectId(request.json.get("org_id")),
    "date": request.json.get("date"),
    "amount": request.json.get("amount"),
  }

  return jsonify({
    "_id": str(get_collection("transactions").insert_one(new_trans).inserted_id),
    "success": True
  }), 201

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
    }), 403
  user = match_list[0]

  company = user["company"]
  orgs = get_collection("orgs")
  orgs_cursor = orgs.find({ "company": company })
  orgs_list = []

  for org in orgs_cursor:
    org["_id"] = str(org["_id"])
    orgs_list.append(org)

  return jsonify({
    "success": True,
    "orgs": orgs_list
  }), 201

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
    }), 403
  user = match_list[0]

  if user["type"] != "full": # access level too little
    return jsonify({
      "success": False
    }), 403

  res = get_collection("orgs").insert_one({
    "company": user["company"],
    "name": request.json.get("name")
  })

  return jsonify({
    "success": True,
    "_id": str(res.inserted_id)
  }), 201

# GET: portfolio positions
@app.route(r("/positions"), methods=["GET"])
@jwt_required()
def get_positions():
  current_user = ObjectId(get_jwt_identity())

  match_cursor = get_collection("users").find({ "_id": current_user })
  match_list = [match for match in match_cursor]
  if len(match_list) != 1: # fake jwt
    return jsonify({
      "success": False,
    }), 403
  user = match_list[0]

  if user["type"] != "full": # no access
    return jsonify({
      "success": False,
    }), 403

  position_cursor = get_collection("positions").find({ "company": user["company"] })
  positions = []
  
  for pos in position_cursor:
    pos["_id"] = str(pos["_id"])
    positions.append(pos)

  stock_ranges = {}
  full_names = {}

  for pos in positions:
    stock_ranges[pos["ticker"]] = utils.get_stock_prices(pos["ticker"], pos["startDate"])

  for pos in positions:
    full_names[pos["ticker"]] = utils.get_company_name(pos["ticker"])

  return jsonify({
    "success": True,
    "positions": positions,
    "ranges": stock_ranges, 
    "names": full_names,
  })

# POST: add position
@app.route(r("/positions"), methods=["POST"])
@jwt_required()
def add_position():
  current_user = ObjectId(get_jwt_identity())
  
  match_cursor = get_collection("users").find({ "_id": current_user })
  match_list = [match for match in match_cursor]
  if len(match_list) != 1:
    return jsonify({
      "success": False,
    }), 403
  user = match_list[0]

  new_pos = {
    "company": user["company"],
    "ticker": request.json.get("ticker"),
    "shares": request.json.get("shares"),
    "initialPrice": request.json.get("initialPrice"),
    "startDate": request.json.get("startDate"),
  }

  return jsonify({
    "_id": str(get_collection("positions").insert_one(new_pos).inserted_id),
    "success": True
  }), 201


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)