from flask import Flask, render_template, request, jsonify
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from bson.objectid import ObjectId

app = Flask(__name__)

db = AsyncIOMotorClient(os.getenv("MONGO")).get_database("anna")
codes_collection = db["login_data"]
users_collection = db["users"]


@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/authenticate")
async def authenticate():
    uuid = request.args.get("code")  # Assuming 'code' refers to the 'uuid' field

    if not uuid:
        return jsonify({"error": "No code provided"}), 400

    # Check if the code (uuid) exists and is unused
    code_document = await codes_collection.find_one({"uuid": uuid, "used": False})

    if code_document:
        # Mark the code as used
        await codes_collection.update_one(
            {"_id": ObjectId(code_document["_id"])}, {"$set": {"used": True}}
        )
        return jsonify(
            {
                "message": f"Authenticated with code: {uuid}",
                "user_id": code_document["user_id"],
            }
        )
    else:
        return jsonify({"error": "Invalid or already used code"}), 401


# 404 Error
@app.errorhandler(404)
def page_not_found(e):
    path = request.path
    return render_template("404.html", path=path), 404


@app.route("/login/<discord_id>")
def login(discord_id):
    return f"Login with Discord ID: {discord_id}"
