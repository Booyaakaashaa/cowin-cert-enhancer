import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session
from werkzeug.utils import secure_filename
import cv2 as cv
import fitz
import copy
import secrets
import string

UPLOAD_FOLDER = 'static/uploads/'
DOWNLOAD_FOLDER = 'static/downloads/'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['SECRET_KEY'] = 'OcQfUw4yBE6QzL5E43JkTw'


@app.route("/")
def index():
    session["code"] = secrets.token_urlsafe(24)
    return redirect(url_for("upload_pdf", hi=session["code"]))


@app.route("/upload_pdf", methods=["POST", "GET"])
def upload_pdf():
    if request.method == "POST":
        f = request.files.get("certificate")
        print(f)
        filename = secure_filename(f.filename)
        if filename.split(".")[-1] == "pdf":
            print("1 " + filename)
            filename = session["code"] + filename
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            pdf_file = fitz.open(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            page = pdf_file[0]
            zoom = 2.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            pix.save(os.path.join(app.config["UPLOAD_FOLDER"], session["code"] + '.png'))
            img = cv.imread(os.path.join(app.config["UPLOAD_FOLDER"], session["code"] + '.png'))

            img[1200:1396, 70:684] = [239, 236, 232]  # Remove PM Photo

            img[1394:1398, 72:684] = [221, 201, 184]  # Repair Line

            img2 = cv.imread("flag.png", cv.IMREAD_UNCHANGED)  # Read Flag art
            dim = (img.shape[1], img.shape[0])

            img2_resize = cv.resize(img2, dim, interpolation=cv.INTER_AREA)  # Resizing Flag Art

            output = copy.deepcopy(img)
            output[:, :] = (img[:, :] / 255) * (img2_resize[:, :] / 255) * 255  # print flag art on pdf
            cv.imwrite(os.path.join(app.config["UPLOAD_FOLDER"], session["code"] + "int_output.png"), output)
            return render_template('upload_pic.html')
    return render_template("upload_cert.html")


@app.route("/upload_pic", methods=["POST", "GET"])
def upload_pic():
    if request.method == "POST":
        f = request.files.get("pic")
        image_name = secure_filename(f.filename)
        print(f, image_name)
        if image_name.split(".")[-1] in ["jpg", "jpeg", "png", "JPG", "JPEG", "PNG"]:
            image_name = session["code"] + image_name
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], image_name))

            img3 = cv.imread(os.path.join(app.config["UPLOAD_FOLDER"], image_name))

            img3 = cv.cvtColor(img3, cv.COLOR_BGR2GRAY)
            img3 = cv.resize(img3, (272, 272), interpolation=cv.INTER_AREA)  # read user image and resize
            img_inv = 255 - img3
            img_blur = cv.GaussianBlur(img_inv, (35, 35), 0)
            output3 = cv.divide(img3, 255 - img_blur, scale=256)
            output3 = cv.cvtColor(output3, cv.COLOR_GRAY2RGB)

            output = cv.imread(os.path.join(app.config["UPLOAD_FOLDER"], session["code"] + "int_output.png"))

            output[1124: 1396, 244: 516] = (output[1124: 1396, 244: 516] / 255) * (output3[:, :] / 255) * 255  # Overlap user photo

            img4 = cv.resize(cv.imread('stamp.png'), (630, 600), interpolation=cv.INTER_AREA)
            output[950: 1550, 0: 630] = (output[950: 1550, 0: 630] / 255) * (img4[:, :] / 255) * 255
            cv.imwrite(os.path.join(app.config["DOWNLOAD_FOLDER"], session["code"] + 'output.png'), output)
            img_pdf = fitz.open()
            image = fitz.open(os.path.join(app.config["DOWNLOAD_FOLDER"], session["code"] + 'output.png'))
            shape = image[0].rect
            pdf_bytes = image.convert_to_pdf()
            image.close()
            img_page = fitz.open("pdf", pdf_bytes)
            page = img_pdf.new_page(width=shape.width, height=shape.height)
            page.show_pdf_page(shape, img_page, 0)
            img_pdf.save(os.path.join(app.config["DOWNLOAD_FOLDER"], session["code"] + "cert_output.pdf"))
            return redirect(url_for("thank_you", output=session["code"] + "cert_output.pdf"))
    return render_template("upload_pic.html")


@app.route("/thank_you/<output>")
def thank_you(output):
    return send_from_directory(app.config["DOWNLOAD_FOLDER"], output, download_name="Certificate.pdf", as_attachment=True, mimetype='application/pdf')


