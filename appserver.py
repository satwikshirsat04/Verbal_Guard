from flask import Flask, request, jsonify, session
from flask_cors import CORS  # Import CORS from flask_cors module
from nltk.sentiment.vader import SentimentIntensityAnalyzer

app = Flask(__name__)
CORS(app)  # Enable CORS for your Flask app
app.secret_key = 'your_secret_key_here'
# Function to write user data to file
def write_user_data(data):
    with open('userdata.txt', 'a') as file:
        file.write(','.join([data.get('username'),  data.get('password'),data.get('email')]) + '\n')


# Function to read user data from file and verify login credentials
def verify_login(username, password):
    with open('userdata.txt', 'r') as file:
        for line in file:
            data = line.strip().split(',')
            print(f"Checking: {data}")  # Debugging statement
            if data[0] == username and data[1] == password:
                return True
    return False

def analyze_sentiment(comment):
    sid = SentimentIntensityAnalyzer()
    scores = sid.polarity_scores(comment)
    compound_score = scores['compound']
    return compound_score

# Function to write user comments to file
def write_comment(comment):
    with open('comments.txt', 'a') as file:
        file.write(comment + '\n')
        


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if username and email:
        write_user_data(data)
        return jsonify({'message': 'User registered successfully'}), 200
    else:
        return jsonify({'error': 'Username or email not provided'}), 400


def load_user_data():
    user_data = {}
    with open('userdata.txt', 'r') as file:
        for line in file:
            # Split the line into parts
            parts = line.strip().split(',')
            if len(parts) == 3:
                username, password, email = parts
                user_data[username] = {'password': password, 'email': email}
            else:
                print(f"Ignoring invalid line: {line}")
    return user_data

users = load_user_data()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username in users and users[username]['password'] == password:
        return jsonify({'message': 'Login successful', 'username': username})
    else:
        return jsonify({'message': 'Invalid username or password'}), 401



@app.route('/post_comment', methods=['POST'])
def post_comment():
    data = request.json
    username = data.get('username')
    comment = data.get('comment')

    if username and comment:
        # Analyze sentiment of the comment
        sentiment_score = analyze_sentiment(comment)
        if sentiment_score < -0.5:
            warning_message = "Warning: Hate speech detected in your comment."
            write_to_file = False
        else:
            warning_message = None
            write_to_file = True

        if write_to_file:
            # Write the comment to the file only if no hate speech detected
            with open('comments.txt', 'a') as file:
                file.write(f"{username}: {comment}\n")

        return jsonify({'message': 'Comment submitted successfully', 'warning_message': warning_message}), 200
    else:
        return jsonify({'message': 'Error: Username or comment missing'}), 400



if __name__ == '__main__':
    app.run(debug=True)
