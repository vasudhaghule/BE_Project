from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from model import validation_generator

app = Flask(__name__)
CORS(app) 

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load the trained model
model_path = 'EmotionDetectionModel.h5'
model = load_model(model_path)

# Define the emotion labels
emotion_labels = ['Angry', 'Fear', 'Happy', 'Neutral', 'Sad']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/classify', methods=['POST'])
def classify_emotion():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'})
    
    files = request.files.getlist('image')
    if len(files) == 0:
        return jsonify({'error': 'No selected files'})

    results = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Load and preprocess the image
            img = image.load_img(filepath, target_size=(48, 48))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array /= 255.0  # Normalize the pixel values to be between 0 and 1

            # Make predictions
            predictions = model.predict(img_array)
            print('predictions:',predictions)

            # Get the emotion label with the highest probability
            predicted_emotion = emotion_labels[np.argmax(predictions)]
            results.append({'emotion': predicted_emotion})
            print("predicted_emotion:",predicted_emotion)
            # Remove the saved file after processing
            os.remove(filepath)

        return jsonify(results)
    

@app.route('/metrics', methods=['GET'])
def get_metrics():
    # Predict emotions for the validation dataset
    summary = model.summary()
    print(summary)
    y_pred = model.predict(validation_generator)
    y_pred_classes = np.argmax(y_pred, axis=1)

    # Get true labels for the validation dataset
    y_true = validation_generator.classes

    # Calculate accuracy score
    accuracy = accuracy_score(y_true, y_pred_classes)
    print("Accuracy:", accuracy)

    # Generate classification report
    class_labels = list(validation_generator.class_indices.keys())
    class_report = classification_report(y_true, y_pred_classes, target_names=class_labels)
    print("\nClassification Report:\n", class_report)

    return jsonify({
        'accuracy': accuracy,
        'classification_report': class_report,
        'model_summary':summary
    })

if __name__ == '__main__':
    # Create the upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
