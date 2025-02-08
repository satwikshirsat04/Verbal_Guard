from flask import Flask, request, jsonify, session
from flask_cors import CORS
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key_here'

# Ensure 'data' directory exists
if not os.path.exists("data"):
    os.makedirs("data")

USERDATA_FILE = "./data/userdata.txt"
COMMENTS_FILE = "./data/comments.txt"

# Function to write user data to file
def write_user_data(data):
    with open(USERDATA_FILE, 'a') as file:
        file.write(','.join([data.get('username'), data.get('password'), data.get('email')]) + '\n')

# Function to load user data and verify login credentials
def load_user_data():
    user_data = {}
    
    if not os.path.exists(USERDATA_FILE):
        open(USERDATA_FILE, 'w').close()  # Create the file if it doesn't exist
    
    with open(USERDATA_FILE, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 3:
                username, password, email = parts
                user_data[username] = {'password': password, 'email': email}
            else:
                print(f"Ignoring invalid line: {line}")
    return user_data

users = load_user_data()

def analyze_sentiment(comment):
    sid = SentimentIntensityAnalyzer()
    scores = sid.polarity_scores(comment)
    return scores['compound']

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if username and email:
        write_user_data(data)
        return jsonify({'message': 'User registered successfully'}), 200
    return jsonify({'error': 'Username or email not provided'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username in users and users[username]['password'] == password:
        return jsonify({'message': 'Login successful', 'username': username})
    return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/post_comment', methods=['POST'])
def post_comment():
    data = request.json
    username = data.get('username')
    comment = data.get('comment')

    if username and comment:
        sentiment_score = analyze_sentiment(comment)
        warning_message = "Warning: Hate speech detected in your comment." if sentiment_score < -0.5 else None
        
        if sentiment_score >= -0.5:
            with open(COMMENTS_FILE, 'a') as file:
                file.write(f"{username}: {comment}\n")

        return jsonify({'message': 'Comment submitted successfully', 'warning_message': warning_message}), 200
    return jsonify({'message': 'Error: Username or comment missing'}), 400

if __name__ == '__main__':
    app.run(debug=True)
