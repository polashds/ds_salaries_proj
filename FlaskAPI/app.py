from flask import Flask, request, jsonify
import numpy as np
import pickle

app = Flask(__name__)

def load_models():
    file_name = "models/model_file.p"
    with open(file_name, 'rb') as pickled:
        data = pickle.load(pickled)
        model = data['model']
    return model

@app.route('/')
def home():
    return "Flask ML model API is running."

@app.route('/predict', methods=['POST'])
def predict():
    try:
        request_json = request.get_json()
        x = request_json['input']
        x_in = np.array(x).reshape(1, -1)
        model = load_models()
        prediction = model.predict(x_in)[0]
        return jsonify({'response': prediction})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    from data_input import data_in
    x_in = np.array(data_in).reshape(1, -1)
    model = load_models()
    prediction = model.predict(x_in)[0]
    return jsonify({'response': prediction})

if __name__ == '__main__':
    app.run(debug=True)
