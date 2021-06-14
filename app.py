import io
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import cv2 as cv
import fitz
import copy
import numpy as np

app = Flask(__name__)


@app.route("/")
def upload():
    return render_template("upload_cert.html")


@app.route("/upload_pic", methods=["POST"])
def upload_pdf():
    if request.method == "POST":
        f = request.files.get("certificate")
        filename = secure_filename(f.filename)
        pdf_file = fitz.open(filename, stream=f.read())
        page = pdf_file[0]
        zoom = 2.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        img = np.ascontiguousarray(img[..., [2, 1, 0]])  # rgb to bgr

        img[1200:1396, 70:684] = [239, 236, 232]  # Remove PM Photo

        img[1394:1398, 72:684] = [221, 201, 184]  # Repair Line

        img2 = cv.imread("flag.png", cv.IMREAD_UNCHANGED)  # Read Flag art
        dim = (img.shape[1], img.shape[0])

        img2_resize = cv.resize(img2, dim, interpolation=cv.INTER_AREA)  # Resizing Flag Art

        output = copy.deepcopy(img)
        output[:, :] = (img[:, :] / 255) * (img2_resize[:, :] / 255) * 255  # print flag art on pdf
        upload_pdf.out = output

        return render_template('upload_pic.html')


@app.route("/thank_you", methods=["POST"])
def upload_pic():
    if request.method == "POST":
        f = request.files.get("pic")

        img3 = f.read()
        img3 = np.frombuffer(img3, np.uint8)
        img3 = cv.imdecode(img3, cv.IMREAD_COLOR)

        img3 = cv.cvtColor(img3, cv.COLOR_BGR2GRAY)
        img3 = cv.resize(img3, (272, 272), interpolation=cv.INTER_AREA) #read user image and resize
        img_inv = 255 - img3
        img_blur = cv.GaussianBlur(img_inv, (35, 35), 0)
        output3 = cv.divide(img3, 255 - img_blur, scale=256)
        output3 = cv.cvtColor(output3, cv.COLOR_GRAY2RGB)

        output = upload_pdf.out

        output[1124: 1396, 244: 516] = (output[1124: 1396, 244: 516] / 255) * (output3[:, :] / 255) * 255  # OVerlap user photo

        img4 = cv.resize(cv.imread('stamp.png'), (630, 600), interpolation=cv.INTER_AREA)
        output[950: 1550, 0: 630] = (output[950: 1550, 0: 630] / 255) * (img4[:, :] / 255) * 255

        _, output_stream = cv.imencode('.png', output)
        output_stream = output_stream.tobytes()

        image = fitz.open("png", stream=output_stream)
        pdf_bytes = image.convert_to_pdf()
        image.close()

        img_pdf = io.BytesIO(pdf_bytes)
        return send_file(img_pdf, download_name="certificate.pdf", as_attachment=True, mimetype='application/pdf')


if __name__ == "__main__":
    app.run(debug=True)
