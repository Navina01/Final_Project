from __future__ import division, print_function
import os
import numpy as np
from flask import Flask, request, render_template, redirect
from werkzeug.utils import secure_filename
from PIL import Image
from keras.models import load_model
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input
import traceback

# Define a flask app
app = Flask(__name__)
model = None

print('Check http://127.0.0.1:5000/')

def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    return preds

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        f = request.form['models']
        print(f)
        if f == 'ML':
            MODEL_PATH = './models/vgg16-Copy1.h5'
            print('loaded vgg16')
        elif f == 'DL':
            MODEL_PATH = './/models//resnet50.h5'
            print('loaded resnet50')
        # elif f == 'Pre':
        #     MODEL_PATH = './models/model_densenet121.h5'
        #     print('loaded densenet121')

        global model
        try:
            model = load_model(MODEL_PATH)
            print("Model loaded successfully")
        except Exception as e:
            print("Error loading the model:", e)
            return "Error loading the model", 500  # Internal Server Error
        return redirect('/')
    return render_template('index.html')

from flask import jsonify  # Import jsonify to return JSON responses

@app.route('/predict', methods=['POST'])
def upload():
    if request.method == 'POST':
        try:
            if model is None:
                raise Exception("Model is not loaded")

            # Get the file from post request
            f = request.files['file']

            # Save the file to ./uploads
            basepath = os.path.dirname(__file__)
            file_path = os.path.join(basepath, 'uploads', secure_filename(f.filename))
            f.save(file_path)

            # Make prediction
            with Image.open(file_path) as imag:
                preds = model_predict(file_path, model)

            # Remove the file after prediction
            os.remove(file_path)

            # Process the result
            pred_class = np.argmax(preds)
            if pred_class == 1:
                result = 'Pneumonia'
            else:
                result = 'Normal'
            print("Prediction:", result)

            # Return prediction result as JSON
            return jsonify(prediction=result)
        except Exception as e:
            traceback.print_exc()
            return jsonify(error=str(e)), 500  # Internal Server Error

if __name__ == '__main__':
    app.run(debug=True)
