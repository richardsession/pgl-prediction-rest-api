# Deploy to Heroku, then Lambdas/S3
# Best security practices in Flask
# Test in Postman
# Test using Python Test Suite

import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from file_manager import FileManager
from predictor import Predictor

load_dotenv()
app = Flask(__name__, root_path='public/')
# app.config['UPLOAD_FOLDER'] = './screenshots'

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/new_model')
def new_model():
    return render_template('new_model.html')

@app.route('/predict', methods=['POST'])
def predict():
    num_results = int(request.form['num_results']) or 5
    f = request.files['screenshot']

    # Upload file to the cloud
    file_manager = FileManager(os.getenv('S3_FILE_BUCKET'), {'image/gif', 'image/png', 'image/jpeg'})
    file = file_manager.upload(f)
    
    # Get classifications based on submitted image
    predictor = Predictor(file, num_results)
    predictions = predictor.get_top_predictions()
    
    # Remove image to not congest file system
    os.remove(file)

    return jsonify(predictions)

@app.route('/upload_new_model', methods=['POST'])
def upload_new_model():
    f = request.files['screenshot']

    file_manager = FileManager(os.getenv('S3_MODEL_BUCKET'), {'application/octet-stream'})
    file = file_manager.upload_new_version(f, 'greenlight_model.pkl')

    return jsonify(file)



if __name__ == '__main__':
    app.run(debug=True)