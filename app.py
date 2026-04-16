from flask import Flask, render_template, request, redirect
import boto3
import pymysql
import os
import uuid

app = Flask(__name__)

# =====================
# S3 CONFIG (AMAN)
# =====================
S3_BUCKET = "sampah1"
S3_REGION = "ap-southeast-2"

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=S3_REGION
)

# =====================
# RDS CONFIG
# =====================
db = pymysql.connect(
    host=os.getenv("DB_HOST"),  
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database="clean_city"
)

# =====================
# HOME
# =====================
@app.route("/")
def index():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM laporan")
        data = cursor.fetchall()
    except:
        data = []
    return render_template("index.html", data=data)

# =====================
# UPLOAD S3 + SAVE DB
# =====================
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files['file']
    lokasi = request.form['lokasi']
    deskripsi = request.form['deskripsi']

    filename = str(uuid.uuid4()) + "-" + file.filename

    # upload ke S3
    s3.upload_fileobj(file, S3_BUCKET, filename)

    url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"

    # simpan ke DB
    try:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO laporan (lokasi, deskripsi, foto, status) VALUES (%s,%s,%s,%s)",
            (lokasi, deskripsi, url, "Pending")
        )
        db.commit()
    except:
        pass

    return redirect("/")

# =====================
# RUN
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)