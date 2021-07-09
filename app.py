import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import cv2 as cv
import fitz
import copy
import secrets

UPLOAD_FOLDER = 'static/uploads/'
DOWNLOAD_FOLDER = 'static/downloads/'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 6 * 1000 * 1000
app.config['SECRET_KEY'] = b'\xc8\xd3\xe1\x97\xd4Q x\xd6\xb1\x9bv=\x8e\xa6\x17M\xd0)\x9d&};\xf4'


@app.errorhandler(RequestEntityTooLarge)
def file_size(e):
    return """
    <p>File size too large!</p>
    <p>Max. acceptable size is 5MB</p>
    <a href="https://cowin-cert-enhancer.herokuapp.com/">Try again!</a>
    """, 413


@app.route("/")
def index():
    session["code"] = secrets.token_urlsafe(24)
    return redirect(url_for("upload_pdf", foobar=session["code"]))


# Operation on PDF
@app.route("/upload_pdf", methods=["POST", "GET"])
def upload_pdf():
    if request.method == "POST":
        f = request.files.get("certificate")
        filename = secure_filename(f.filename)
        if filename.split(".")[-1] == "pdf":

            f.save(os.path.join(app.config["UPLOAD_FOLDER"], session["code"] + filename))
            f.close()

            pdf_file = fitz.open(os.path.join(app.config["UPLOAD_FOLDER"], session["code"] + filename))
            page = pdf_file[0]  # Read first page of PDF file
            zoom = 2.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)  # Convert PDF page to PNG
            pix.save(os.path.join(app.config["UPLOAD_FOLDER"], session["code"] + '.png'))
            img = cv.imread(os.path.join(app.config["UPLOAD_FOLDER"], session["code"] + '.png'))
            pdf_file.close()

            img[1200:1396, 70:684] = [239, 236, 232]  # Remove PM photo

            img[1394:1398, 72:684] = [221, 201, 184]  # Repair blue line below PM

            img2 = cv.imread("flag.png", cv.IMREAD_UNCHANGED)
            dim = (img.shape[1], img.shape[0])

            img2_resize = cv.resize(img2, dim, interpolation=cv.INTER_AREA)

            output = copy.deepcopy(img)
            output[:, :] = (img[:, :] / 255) * (img2_resize[:, :] / 255) * 255  # Superimpose flag art on certificate
            cv.imwrite(os.path.join(app.config["UPLOAD_FOLDER"], session["code"] + "int_output.png"), output)

            os.remove(os.path.join(app.config["UPLOAD_FOLDER"], session["code"] + ".png"))
            os.remove(os.path.join(app.config["UPLOAD_FOLDER"], session["code"] + filename))

            return redirect(url_for('upload_pic', foobar=session["code"]))
        else:
            return """<p>File extension not allowed!</p><br><p>Upload PDF Certificate</p><br>
            <a id="retry" href="https://cowin-cert-enhancer.herokuapp.com/">Try again!</a>"""
    return render_template("upload_cert.html")


# Operation on Selfie
@app.route("/upload_pic", methods=["POST", "GET"])
def upload_pic():
    if request.method == "POST":
        f = request.files.get("pic")
        image_name = secure_filename(f.filename)
        if image_name.split(".")[-1] in ["jpg", "jpeg", "png", "JPG", "JPEG", "PNG"]:
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], session["code"] + image_name))
            f.close()

            img3 = cv.imread(os.path.join(app.config["UPLOAD_FOLDER"], session["code"] + image_name))

            # Sketchify selfie
            img3 = cv.cvtColor(img3, cv.COLOR_BGR2GRAY)
            img3 = cv.resize(img3, (272, 272), interpolation=cv.INTER_AREA)
            img_inv = 255 - img3
            img_blur = cv.GaussianBlur(img_inv, (35, 35), 0)
            output3 = cv.divide(img3, 255 - img_blur, scale=256)
            output3 = cv.cvtColor(output3, cv.COLOR_GRAY2RGB)

            output = cv.imread(os.path.join(app.config["UPLOAD_FOLDER"], session["code"] + "int_output.png"))

            # Superimpose selfie on certificate
            output[1124: 1396, 244: 516] = (output[1124: 1396, 244: 516] / 255) * (output3[:, :] / 255) * 255

            # Final PDF generation
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

            os.remove(os.path.join(app.config["UPLOAD_FOLDER"], session["code"] + "int_output.png"))
            os.remove(os.path.join(app.config["UPLOAD_FOLDER"], session["code"] + image_name))

            return redirect(url_for("thank_you", output=session["code"]))
        else:
            return """<p>File extension not allowed!</p><p>Upload JPEG/JPG/PNG Selfie</p>
            <a href="https://cowin-cert-enhancer.herokuapp.com/">Try again!</a>"""
    return render_template("upload_pic.html")


@app.route("/thank_you/<output>")
def thank_you(output):
    return render_template("thank_you.html", output=output + "output.png")


@app.route("/download")
def download_cert():
    return send_from_directory(app.config["DOWNLOAD_FOLDER"], session["code"] + "cert_output.pdf", download_name="Certificate.pdf", as_attachment=True, mimetype='application/pdf')
