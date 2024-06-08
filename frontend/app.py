import os
from flask import Flask, redirect, url_for, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import matplotlib.pyplot as plt
from flask_cors import CORS
from PIL import Image
import io
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_PATH'] = 'static/uploads'
app.config['PREDICTED_PATH'] = 'static/predicted'
app.secret_key = 'your_secret_key'  # Change this to a secret key for session management

# Load the model
mdl = tf.keras.models.load_model('modl.h5')

def predict_image(image_path):
    # Load and preprocess the input image
    img = load_img(image_path, target_size=(256, 256))  # Assuming your model expects input shape (256, 256)
    img_array = img_to_array(img) / 255.0  # Normalize the pixel values

    # Make prediction
    predicted_image = mdl.predict(np.expand_dims(img_array, axis=0))[0]

    # Post-process the predicted image if necessary (e.g., thresholding)
    # For example, if your model outputs probabilities, you might apply a threshold to convert it to binary mask
    predicted_binary = (predicted_image > 0.5).astype(np.uint8)

    # Normalize the predicted image pixel values to the range of 0 to 1
    normalized_predicted_image = (predicted_image - predicted_image.min()) / (predicted_image.max() - predicted_image.min())
    # Save the predicted image
    predicted_image_path = os.path.join('static/predicted/', os.path.basename(image_path))  
    plt.imsave(predicted_image_path, predicted_image, cmap='gray')  
    
    return predicted_image_path

@app.route('/login')
def login():
    return render_template('login.html')

@app.route("/")
def index():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    uploads_dir = 'static/uploads/'
    uploads = sorted(os.listdir(uploads_dir), key=lambda x: os.path.getctime(uploads_dir + x))
    uploads.reverse()
    uploads = ['uploads/' + file for file in uploads]
    return render_template("index.html", uploads=uploads)

@app.route('/login', methods=['POST'])
def authenticate():
    username = request.form['username'].strip()  # Ensure leading/trailing white spaces are removed
    password = request.form['password'].strip()  
    print("Received username:", username)
    print("Received password:", password)
    if username == 'admin' and password == 'password':
        session['logged_in'] = True
        return redirect(url_for('index'))
    else:
        return 'Invalid username or password. Please try again.'

@app.route("/upload", methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_PATH'], filename)
            file.save(file_path)

            # Load the uploaded image and normalize it
            img = Image.open(file_path)
            img_array = np.array(img) / 255.0  # Normalize pixel values to the range of 0 to 1

            # Save the normalized image temporarily
            normalized_img_path = os.path.join(app.config['UPLOAD_PATH'], 'normalized_' + filename)
            plt.imsave(normalized_img_path, img_array, cmap='gray')

            return jsonify({'uploaded_image_path': normalized_img_path})

    return jsonify({'error': 'Upload failed'})

@app.route("/predict", methods=['POST'])
def predict():
    if request.method == 'POST':
        image_path = request.form.get('image_path')
        if not image_path:
            return jsonify({'error': 'No image path provided'})

        # Call the predict_image function to get the path of the predicted image
        predicted_image_path = predict_image(image_path)
        if predicted_image_path:
            return jsonify({'predicted_image_path': predicted_image_path})
        else:
            return jsonify({'error': 'Prediction failed'})

@app.route("/remove", methods=['POST'])
def remove_file():
    if request.method == 'POST':
        image_path = request.form['image_path']
        if os.path.exists(image_path):
            os.remove(image_path)
        return jsonify({'message': 'File removed successfully'})

if __name__ == "__main__":
    app.run(debug=True)
