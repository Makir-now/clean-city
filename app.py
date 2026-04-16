from flask import Flask, render_template, request, redirect
import boto3
import pymysql
import os

app = Flask(__name__)

# =====================
# CONFIG S3 (AWS)
# =====================
S3_BUCKET = "sampah1"
S3_REGION = "ap-southeast-2"

s3 = boto3.client(
    "s3",
    region_name=S3_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

# =====================
# CONFIG RDS (AWS)
# =====================
db = pymysql.connect(
    host=os.getenv("DB_HOST"),   # endpoint RDS nanti
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database="clean_city",
    cursorclass=pymysql.cursors.Cursor
)

# =====================
# ROUTES
# =====================
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

    # Upload ke S3
    s3.upload_fileobj(file, S3_BUCKET, filename)

    url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"

    # Simpan ke RDS
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO laporan (lokasi, deskripsi, foto, status) VALUES (%s,%s,%s,%s)",
        (lokasi, deskripsi, url, "Pending")
    )
    db.commit()

    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)