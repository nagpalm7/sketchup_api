from flask import Flask, request, jsonify, send_file
import cv2
import os
from werkzeug.utils import secure_filename
from flask_api import status

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'svg'])
UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/filter/sketch/', methods=['POST'])
def post_something():
    if 'image' not in request.files:
        msg = jsonify({
            "Error": "No image (file) uploaded.",
        })
        return msg , status.HTTP_400_BAD_REQUEST

    file = request.files['image']
    if file and file.filename.split('.')[1] in ALLOWED_EXTENSIONS:
        if not os.path.exists(app.config['UPLOAD_FOLDER'],):
            os.makedirs(app.config['UPLOAD_FOLDER'],)
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        img = cv2.imread(path)
        # Convert the image into grayscale image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Blur the image using Gaussian Blur 
        gray_blur = cv2.GaussianBlur(gray, (25, 25), 0)
        # Convert the image into pencil sketch
        scale = 250.0
        if request.form.get('scale'):
            try:
                scale = float(request.form.get('scale'))
            except Exception:
                msg = jsonify({
                    "Error": "Please set an float scale between 1 to 300",
                })
                return msg , status.HTTP_400_BAD_REQUEST


        cartoon = cv2.divide(gray, gray_blur, scale=scale)
        cv2.imwrite(path, cartoon)
        return send_file(path, mimetype='image/png')
    else:
        msg = jsonify({
            "Error": "Please upload a valid png, jpg or jpeg file.",
        })
        return msg , status.HTTP_400_BAD_REQUEST

    if True:
        return jsonify({
            "Message": f"Welcome to our awesome platform!!",
        })
    else:
        return jsonify({
            "ERROR": "Invalid File"
        })

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>penIT :- Welcome to our server !!</h1>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)