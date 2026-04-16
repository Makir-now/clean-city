from flask import Flask, render_template, request, redirect
import boto3
import pymysql
import os

app = Flask(__name__)

# CONFIG AWS
S3_BUCKET = "nama-bucket-kamu"
s3 = boto3.client('s3')

# CONFIG RDS
db = pymysql.connect(
    host="localhost",
    user="root",
    password="",  # kalau ada password isi
    database="clean_city"
)

@app.route("/")
def index():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM laporan")
    data = cursor.fetchall()
    return render_template("index.html", data=data)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files['file']
    lokasi = request.form['lokasi']
    deskripsi = request.form['deskripsi']

    filename = file.filename
    s3.upload_fileobj(file, S3_BUCKET, filename)

    url = f"https://{S3_BUCKET}.s3.amazonaws.com/{filename}"

    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO laporan (lokasi, deskripsi, foto, status) VALUES (%s,%s,%s,%s)",
        (lokasi, deskripsi, url, "Pending")
    )
    db.commit()

    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)