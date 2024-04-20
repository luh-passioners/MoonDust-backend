from flask import Flask, jsonify
from flask_cors import CORS
from db import get_collection

app = Flask(__name__)
CORS(app)

API_PREFIX = "/api/v1"
def r(endpoint):
  return f"{API_PREFIX}{endpoint}"

@app.route(r("/transactions"), methods=["GET"])
def get_transactions():
  trans = get_collection("transactions").find()
  
  jsonable_trans = [{
    "_id": str(item["_id"]),
    "names": item["name"],
    "org_id": item["org_id"],
    "date": item["date"],
    "amount": item["amount"]
  } for item in trans]

  return jsonify(jsonable_trans)

@app.route(r("/transactions"), methods=["POST"])
def add_transaction():
  new_trans = {
    "name": "Fortnite battle pass",
    "org_id": 12,
    "date": "2024-12-31",
    "amount": -9.99,
  }

  return jsonify({
    "_id": str(get_collection("transactions").insert_one(new_trans).inserted_id)
  })

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)