# ============================================================
# PYMONGO — MongoDB with Python — Interview Essentials
# ============================================================
# pip install pymongo

import pymongo
from bson import ObjectId
from datetime import datetime

# ── CONNECT ──────────────────────────────────────────────────
client = pymongo.MongoClient("mongodb://localhost:27017")
db     = client["mydb"]           # access database
col    = db["users"]              # access collection (creates if not exists)

# ── INSERT ────────────────────────────────────────────────────
# insert_one — insert a single document
result = col.insert_one({
    "name":       "Chaman",
    "email":      "c@y.com",
    "age":        21,
    "isActive":   True,
    "createdAt":  datetime.utcnow()
})
print(result.inserted_id)   # the _id of the inserted document

# insert_many — insert multiple documents
result = col.insert_many([
    {"name": "Alice", "age": 25, "email": "a@y.com"},
    {"name": "Bob",   "age": 30, "email": "b@y.com"}
])
print(result.inserted_ids)   # list of _ids

# ── FIND ─────────────────────────────────────────────────────
# find_one — returns dict or None
user = col.find_one({"email": "c@y.com"})
print(user)

# find — returns cursor (iterate to get results)
cursor = col.find({"isActive": True})
for user in cursor:
    print(user["name"])

# Comparison operators
adults = col.find({"age": {"$gt": 18}})            # age > 18
range_users = col.find({"age": {"$gte": 18, "$lte": 30}})  # 18 <= age <= 30

# List operators
users_in = col.find({"name": {"$in": ["Alice", "Bob"]}})    # name IN list
users_nin = col.find({"name": {"$nin": ["Charlie"]}})       # name NOT IN list

# exists
with_phone = col.find({"phone": {"$exists": True}})

# Projection — what fields to return
names_only = col.find(
    {"isActive": True},
    {"name": 1, "email": 1, "_id": 0}   # 1=include, 0=exclude
)

# Sort, skip, limit (for pagination)
paginated = col.find().sort("name", pymongo.ASCENDING).skip(0).limit(10)

# Count
count = col.count_documents({"isActive": True})

# ── UPDATE ────────────────────────────────────────────────────
# update_one — update first matching document
result = col.update_one(
    {"email": "c@y.com"},           # filter
    {"$set": {"name": "Chaman V2", "age": 22}}   # update
)
print(result.modified_count)   # how many documents were changed

# update_many — update all matching documents
col.update_many(
    {"isActive": False},
    {"$set": {"archived": True}}
)

# Other operators
col.update_one({"_id": ObjectId("...")}, {"$push": {"tags": "python"}})  # add to array
col.update_one({"_id": ObjectId("...")}, {"$pull": {"tags": "old"}})     # remove from array
col.update_one({"_id": ObjectId("...")}, {"$inc": {"loginCount": 1}})    # increment
col.update_one({"_id": ObjectId("...")}, {"$unset": {"oldField": ""}})   # remove field

# upsert — insert if not found, update if found
col.update_one(
    {"email": "new@y.com"},
    {"$set": {"name": "New User", "email": "new@y.com"}},
    upsert=True
)

# ── DELETE ────────────────────────────────────────────────────
col.delete_one({"email": "c@y.com"})
col.delete_many({"isActive": False, "archived": True})

# ── AGGREGATION ───────────────────────────────────────────────
pipeline = [
    # $match: filter documents (like WHERE)
    {"$match": {"isActive": True}},

    # $group: group documents + calculate
    {"$group": {
        "_id":       "$role",          # group by role
        "count":     {"$sum": 1},      # count
        "avgAge":    {"$avg": "$age"},  # average age
        "names":     {"$push": "$name"} # collect names into array
    }},

    # $sort: sort results
    {"$sort": {"count": -1}},

    # $limit: top N
    {"$limit": 5}
]

results = col.aggregate(pipeline)
for group in results:
    print(group)


# $lookup: JOIN with another collection
posts_col = db["posts"]
pipeline_with_join = [
    {"$match": {"isActive": True}},
    {
        "$lookup": {
            "from":         "posts",   # other collection
            "localField":   "_id",     # field in users
            "foreignField": "author",  # field in posts
            "as":           "posts"    # output field name
        }
    },
    {
        "$project": {
            "name":      1,
            "email":     1,
            "postCount": {"$size": "$posts"}  # count of posts
        }
    }
]

# ── INDEXES ───────────────────────────────────────────────────
col.create_index("email", unique=True)            # unique index
col.create_index([("name", pymongo.ASCENDING)])   # regular index
col.create_index([("age", pymongo.DESCENDING), ("name", pymongo.ASCENDING)])  # compound

# Text search index
col.create_index([("name", "text"), ("bio", "text")])
results = col.find({"$text": {"$search": "chaman"}})

client.close()
