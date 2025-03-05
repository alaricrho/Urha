from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from functools import wraps
# from firebase_config import firebase_admin
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# cred = credentials.Certificate("FIREBASE_CREDENTIALS")
# firebase_admin.initialize_app(cred)

firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')

if not firebase_credentials:
    raise ValueError("FIREBASE_CREDENTIALS environment variable is not set.")

# Use the credentials directly (no need for json.loads or a file path)
cred = credentials.Certificate(firebase_credentials)

# Initialize Firebase Admin
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()
# QUIZ_FILE = 'quizzes.json'

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response
    
# def load_data(file_path):
#     """Load quiz data from the JSON file."""
#     try:
#         with open(file_path, 'r') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return []  # Return an empty list instead of {} if the file doesn't exist

def load_data():
    """Load quiz data from Firestore."""
    quizzes_ref = db.collection("quizzes")  # Reference to the 'quizzes' collection
    docs = quizzes_ref.stream()  # Get all documents in the collection

    quizzes = []
    for doc in docs:
        quizzes.append(doc.to_dict())  # Convert each document to a dictionary

    return quizzes


# def save_data(data, file_path):
#     """Save quiz data to the JSON file."""
#     with open(file_path, 'w') as f:
#         json.dump(data, f, indent=4)

def save_data(data):
    """Save quiz data to Firestore."""
    quizzes_ref = db.collection("quizzes")  # Reference to the 'quizzes' collection
    
    for quiz in data:
        quiz_ref = quizzes_ref.document(quiz['quiz_name'])  # Use quiz name as document ID
        quiz_ref.set(quiz)  # Save quiz document to Firestore


def login_required(f):
    """Decorator to check if the user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'jermyshijo' and password == '7dc6d58aec12':
            session['username'] = username
            return redirect(url_for('admin'))
        else:
            return 'Invalid credentials', 401
    return render_template('login.html')

# @app.route('/admin')
# @login_required
# def admin():
#     quizzes = load_data(QUIZ_FILE)
#     return render_template('admin.html', quizzes=quizzes)

### THis is the original one oka
# @app.route('/admin')
# @login_required
# def admin():
#     quizzes = load_data(QUIZ_FILE)
    
#     # Convert the list of quizzes into a dictionary where keys are quiz names
#     quizzes_dict = {quiz['quiz_name']: quiz['questions'] for quiz in quizzes}
    
#     return render_template('admin.html', quizzes=quizzes_dict)
### TIll here

@app.route('/admin')
@login_required
def admin():
    quizzes = load_data()  # Fetch quizzes from Firestore
    
    # Convert the list of quizzes into a dictionary where keys are quiz names
    quizzes_dict = {quiz['quiz_name']: quiz['questions'] for quiz in quizzes}
    
    return render_template('admin.html', quizzes=quizzes_dict)

# @app.route('/admin/get_quiz/<quiz_name>')
# @login_required
# def get_quiz(quiz_name):
#     """Retrieve a specific quiz."""
#     quizzes = load_data(QUIZ_FILE)
#     quiz = quizzes.get(quiz_name)

#     if quiz:
#         return jsonify({"name": quiz_name, "questions": quiz})
#     else:
#         return jsonify({"error": "Quiz not found"}), 404


### Original is here
# @app.route('/admin/get_quiz/<quiz_name>')
# @login_required
# def get_quiz(quiz_name):
#     """Retrieve a specific quiz."""
#     quizzes = load_data(QUIZ_FILE)
    
#     # Find the quiz in the list
#     quiz = next((quiz for quiz in quizzes if quiz['quiz_name'] == quiz_name), None)

#     if quiz:
#         return jsonify({
#             "quiz_name": quiz['quiz_name'],
#             "language": quiz['language'],
#             "questions": quiz['questions']
#         })
#     else:
#         return jsonify({"error": "Quiz not found"}), 404
### Till here

@app.route('/admin/get_quiz/<quiz_name>')
@login_required
def get_quiz(quiz_name):
    """Retrieve a specific quiz."""
    # Fetch quizzes from Firestore
    quizzes = load_data()  # Load quizzes from Firestore
    
    # Find the quiz by its name
    quiz = next((quiz for quiz in quizzes if quiz['quiz_name'] == quiz_name), None)

    if quiz:
        return jsonify({
            "quiz_name": quiz['quiz_name'],
            "language": quiz['language'],
            "questions": quiz['questions']
        })
    else:
        return jsonify({"error": "Quiz not found"}), 404



# @app.route('/admin/edit', methods=['GET', 'POST'])    
# @login_required
# def create_or_edit_quiz():
#     """Create or edit a quiz."""
#     if request.method == 'POST':
#         quiz_name = request.form['quiz_name']
#         questions = []

#         for i in range(1, 1000000):  # Allow up to 10 questions
#             question = request.form.get(f'question-{i}')
#             answer = request.form.get(f'answer-{i}')
#             if question and answer:  # Skip empty question-answer pairs
#                 questions.append({'question': question, 'answer': answer})

#         quizzes = load_data(QUIZ_FILE)
#         quizzes[quiz_name] = questions
#         save_data(quizzes, QUIZ_FILE)

#         return redirect(url_for('admin'))

#     quiz_name = request.args.get('quiz_name')
#     quizzes = load_data(QUIZ_FILE)
#     current_questions = quizzes.get(quiz_name, []) if quiz_name else []

#     return render_template('admin_edit.html', quiz_name=quiz_name, current_questions=current_questions)


### This is original part okay


# @app.route('/admin/edit', methods=['GET', 'POST'])
# @login_required
# def create_or_edit_quiz():
#     if request.method == 'POST':
#         quiz_name = request.form['quiz_name']
#         language = request.form['language']  # Get the selected language
#         questions = []

#         # Collect the questions and answers
#         for i in range(1, 1000000):
#             question = request.form.get(f'question-{i}')
#             answer = request.form.get(f'answer-{i}')
#             if question and answer:
#                 questions.append({'question': question, 'answer': answer})

#         # Load existing quizzes
#         quizzes = load_data(QUIZ_FILE)
        
#         # Check if we are editing an existing quiz or creating a new one
#         if quiz_name in [quiz['quiz_name'] for quiz in quizzes]:
#             for quiz in quizzes:
#                 if quiz['quiz_name'] == quiz_name:
#                     quiz['language'] = language
#                     quiz['questions'] = questions
#                     break
#         else:
#             quizzes.append({
#                 'quiz_name': quiz_name,
#                 'language': language,
#                 'questions': questions
#             })
        
#         save_data(quizzes, QUIZ_FILE)

#         return redirect(url_for('admin'))

#     quiz_name = request.args.get('quiz_name')
#     quizzes = load_data(QUIZ_FILE)
#     current_quiz = next((quiz for quiz in quizzes if quiz['quiz_name'] == quiz_name), None)

#     current_questions = current_quiz['questions'] if current_quiz else []

#     return render_template('admin_edit.html', quiz_name=quiz_name, current_questions=current_questions)

### Till here

@app.route('/admin/edit', methods=['GET', 'POST'])
@login_required
def create_or_edit_quiz():
    if request.method == 'POST':
        quiz_name = request.form['quiz_name']
        language = request.form['language']  # Get the selected language
        questions = []

        # Collect the questions and answers
        for i in range(1, 10000):  # Allow a large range
            question = request.form.get(f'question-{i}')
            answer = request.form.get(f'answer-{i}')
            if question and answer:
                questions.append({'question': question, 'answer': answer})

        quizzes = load_data()  # Get quizzes from Firestore
        
        # Check if we are editing an existing quiz or creating a new one
        quiz_found = False
        for quiz in quizzes:
            if quiz['quiz_name'] == quiz_name:
                quiz['language'] = language
                quiz['questions'] = questions
                quiz_found = True
                break

        if not quiz_found:
            # If the quiz doesn't exist, create a new one
            quizzes.append({
                'quiz_name': quiz_name,
                'language': language,
                'questions': questions
            })
        
        save_data(quizzes)  # Save the updated quizzes to Firestore
        return redirect(url_for('admin'))

    quiz_name = request.args.get('quiz_name')
    quizzes = load_data()
    current_quiz = next((quiz for quiz in quizzes if quiz['quiz_name'] == quiz_name), None)

    current_questions = current_quiz['questions'] if current_quiz else []

    return render_template('admin_edit.html', quiz_name=quiz_name, current_questions=current_questions)


### Original here
# @app.route('/admin/delete/<quiz_name>', methods=['GET'])
# @login_required
# def delete_quiz(quiz_name):
#     """Delete a quiz."""
#     quizzes = load_data(QUIZ_FILE)
#     if quiz_name in quizzes:
#         del quizzes[quiz_name]
#         save_data(quizzes, QUIZ_FILE)

#     return redirect(url_for('admin'))
### Till Here

@app.route('/admin/delete/<quiz_name>', methods=['GET'])
@login_required
def delete_quiz(quiz_name):
    """Delete a quiz from Firestore."""
    quizzes_ref = db.collection("quizzes")  # Reference to the quizzes collection
    quiz_ref = quizzes_ref.document(quiz_name)  # Use quiz name as the document ID
    
    # Delete the quiz document from Firestore
    quiz_ref.delete()

    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    """Logout the user."""
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/language-select')
def language_select():
    return render_template('language_select.html')


### Original here
# @app.route('/quizzes')
# def quizzes():
#     lang = request.args.get('lang', 'english').lower()
#     all_quizzes = load_data(QUIZ_FILE)

#     # Filter quizzes by language
#     filtered_quizzes = [q for q in all_quizzes if q['language'].lower() == lang]
#     print("Filtered quizzes:", filtered_quizzes)
#     return render_template('quizzes.html', quizzes=filtered_quizzes, selected_language=lang)

### Till here

@app.route('/quizzes')
def quizzes():
    lang = request.args.get('lang', 'english').lower()
    all_quizzes = load_data()  # Load quizzes from Firestore

    # Filter quizzes by language
    filtered_quizzes = [q for q in all_quizzes if q['language'].lower() == lang]
    print("Filtered quizzes:", filtered_quizzes)
    return render_template('quizzes.html', quizzes=filtered_quizzes, selected_language=lang)

#### Original here
# @app.route('/quiz/<quiz_name>')
# def quiz(quiz_name):
#     # Load your quiz data
#     quizzes = load_data(QUIZ_FILE)

#     # Find the quiz by name and get its questions
#     selected_quiz = next((quiz for quiz in quizzes if quiz['quiz_name'] == quiz_name), None)
#     if not selected_quiz:
#         return "Quiz not found!", 404

#     # Get the current question index
#     question_index = int(request.args.get('question', 0))
#     question_index = max(0, min(question_index, len(selected_quiz['questions']) - 1))

#     # Calculate progress
#     total_questions = len(selected_quiz['questions'])
#     progress = ((question_index + 1) / total_questions) * 100

#     # Get the language from the request or use the quiz's language
#     selected_language = request.args.get('lang', selected_quiz.get('language', 'english'))

#     # Render template with variables
#     return render_template(
#         'quiz_navigation.html',
#         quiz_name=quiz_name,
#         question=selected_quiz['questions'][question_index],
#         question_index=question_index,
#         total_questions=total_questions,
#         progress=progress,
#         selected_language=selected_language  # Pass the selected language correctly
#     )
#### Till here
@app.route('/quiz/<quiz_name>')
def quiz(quiz_name):
    # Load your quiz data from Firestore
    quizzes = load_data()

    # Find the quiz by name and get its questions
    selected_quiz = next((quiz for quiz in quizzes if quiz['quiz_name'] == quiz_name), None)
    if not selected_quiz:
        return "Quiz not found!", 404

    # Get the current question index
    question_index = int(request.args.get('question', 0))
    question_index = max(0, min(question_index, len(selected_quiz['questions']) - 1))

    # Calculate progress
    total_questions = len(selected_quiz['questions'])
    progress = ((question_index + 1) / total_questions) * 100

    # Get the language from the request or use the quiz's language
    selected_language = request.args.get('lang', selected_quiz.get('language', 'english'))

    # Render template with variables
    return render_template(
        'quiz_navigation.html',
        quiz_name=quiz_name,
        question=selected_quiz['questions'][question_index],
        question_index=question_index,
        total_questions=total_questions,
        progress=progress,
        selected_language=selected_language  # Pass the selected language correctly
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use Railway's PORT or default to 5000
    app.run(host='0.0.0.0', port=port)
