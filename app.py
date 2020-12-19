from flask import Flask, request, jsonify, send_file
import cv2
import os
from werkzeug.utils import secure_filename
from flask_api import status
import numpy as np

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
        img = cv2.imread(path, -1)
        scale = 250.0
        if request.form.get('scale'):
            try:
                scale = float(request.form.get('scale'))
            except Exception:
                msg = jsonify({
                    "Error": "Please set an float scale between 1 to 300",
                })
                return msg , status.HTTP_400_BAD_REQUEST
        if img.shape[2] > 3:
            alpha = img[:,:,3]
            rgb = img[:,:,:-1]
            gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            rgb_gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            alpha = np.reshape(alpha, (*alpha.shape,1))
            gray_alpha = np.concatenate([rgb_gray, alpha], axis=2)
            gray_blur = cv2.GaussianBlur(gray_alpha, (31, 31), 0)
            cartoon = cv2.divide(gray_alpha, gray_blur, scale=scale)
        else:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            gray_blur = cv2.GaussianBlur(gray, (31, 31), 0)
            cartoon = cv2.divide(gray, gray_blur, scale=scale)

        cv2.imwrite(path, cartoon)
        return send_file(path, mimetype='image/png')
    else:
        msg = jsonify({
            "Error": "Please upload a valid png, jpg or jpeg file.",
        })
        return msg , status.HTTP_400_BAD_REQUEST

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>penIT :- Welcome to our server !!</h1>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)