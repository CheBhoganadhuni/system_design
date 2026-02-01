import os, gridfs, pika, json, io
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId

server = Flask(__name__)

# Initialize MongoDB Connections
# We specify the URIs directly to ensure they stay separate
mongo_video = PyMongo(server, uri=os.environ.get("MONGO_URI"))
mongo_mp3s = PyMongo(server, uri=os.environ.get("MONGO_MP3S_URI"))

fs_video = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3s.db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()
 
@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token, 200
    else:
        return err

@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access)

    if access.get("admin"):
        if len(request.files) > 1 or request.files is None:
            return "Please upload only one file", 400
        
        for _, f in request.files.items():
            err = util.upload(f, fs_video, channel, access)
            if err[0]:
                return err
        
        return "File uploaded successfully", 200
    else:
        return "Not authorized", 401

@server.route("/download", methods=["GET"])
def download():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access)

    if access.get("admin"):
        fid_string = request.args.get("fid")
        if not fid_string:
            return "Missing file ID", 400
        
        try:
            # Get the file from GridFS
            out = fs_mp3s.get(ObjectId(fid_string))
            
            # Use io.BytesIO to wrap the binary data. 
            # This is safer for Flask's send_file than passing the GridOut object directly.
            return send_file(
                io.BytesIO(out.read()),
                download_name=f"{fid_string}.mp3",
                mimetype="audio/mp3"
            )
        except Exception as e:
            print(f"Error downloading file: {e}")
            return str(e), 500
    else:
        return "Not authorized", 401

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
    