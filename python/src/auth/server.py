import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL
from dotenv import load_dotenv

load_dotenv()   
server = Flask(__name__)

server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = os.environ.get("MYSQL_PORT")

mysql = MySQL(server)
#print(os.environ.get("MYSQL_HOST"))
#print(os.environ.get("MYSQL_USER"))
#print(os.environ.get("MYSQL_PASSWORD"))
#print(os.environ.get("MYSQL_DB"))
#print(os.environ.get("MYSQL_PORT"))

@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "Missing credentials", 401
    
    # check db for username and pwd
    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT email, password FROM user WHERE email = %s",
        (auth.username,)
    )
    
    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]
        
        if email != auth.username or password != auth.password:
            return "Invalid credentials", 401
        else:
            return "Login successful", 200
    else:
        return "Invalid credentials", 401