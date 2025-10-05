from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/interview')
def interview():
    return app.send_static_file('interview.html')

@app.route('/report')
def report():
    return app.send_static_file('report.html')

# Example API endpoint for saving interview data (optional, can be expanded)
@app.route('/api/save', methods=['POST'])
def save_data():
    data = request.json
    # Here you could save data to a file or database
    return jsonify({'status': 'success', 'data': data})

if __name__ == '__main__':
    app.run(debug=True)
