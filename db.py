from pymongo import MongoClient
import keys

CONNECTION_STRING = f"mongodb+srv://{keys.MONGO_USER}:{keys.MONGO_PASS}@cluster0.xhwgckk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(CONNECTION_STRING)
_db = client["fsm_main"]

def get_collection(name):
  return _db[name]