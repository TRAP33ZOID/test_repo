from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, session
import fitz  # PyMuPDF
import openai
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flaskext.mysql import MySQL

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'flaskapp'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Waleed@1999'
app.config['MYSQL_DATABASE_DB'] = 'test_1'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql = MySQL()
mysql.init_app(app)

UPLOAD_FOLDER ='C:\\Users\\Waleed\\Desktop\\database\\pdf'
ALLOWED_EXTENSIONS = {'pdf'}  # allowed file types

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size
app.secret_key = os.getenv('SECRET_KEY')  # Use environment variable for secret key
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Insert the new user into the database
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
        conn.commit()
        cursor.close()
        conn.close()

        # Redirect to the login page
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form['username']
        password = request.form['password']

        # Connect to the database
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Execute query to find user by username
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        print(f"Fetched User: {user}")  # Debug print

        # Check if user exists and password matches
        if user and user[3] == password:  
            # User is authenticated
            print("Login successful")  # Debug print
            session['logged_in'] = True
            session['username'] = user[1]  
            flash('You were successfully logged in', 'success')
            return redirect(url_for('index'))  # Redirect to the index page or dashboard
        else:
            # Invalid credentials
            print("Login failed")  # Debug print
            flash('Wrong login credentials', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/summarize', methods=['POST'])
def summarize():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Check if file exists to avoid overwriting
        counter = 1
        while os.path.exists(save_path):
            name, extension = os.path.splitext(filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{name}_{counter}{extension}")
            counter += 1

        file.save(save_path)

        extracted_text = extract_text_pymupdf(save_path)
        summary = summarize_text(extracted_text)
        os.unlink(save_path)  
        return jsonify({"summary": summary, "extractedText": extracted_text[:500]})
    else:
        return jsonify({"error": "Invalid file type or no file uploaded"}), 400

def extract_text_pymupdf(pdf_file_path):
    doc = fitz.open(pdf_file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def summarize_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": "Please summarize this text considering the following points: Type of Insurance, Category of Coverage, What's Covered, What's Not Covered, Events Covered, and Additional Details."},
            {"role": "user", "content": text}
        ]
    )
    return response['choices'][0]['message']['content']

if __name__ == '__main__':
    app.run(debug=True)
