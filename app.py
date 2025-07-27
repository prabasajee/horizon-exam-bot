"""
Flask API for Horizon Exam Bot
Handles PDF/DOCX uploads, text extraction, quiz creation, and quiz management
"""

import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
from typing import Dict, List, Any

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# Store for quiz sessions (in production, use a database)
quiz_sessions = {}


class DocumentProcessor:
    """Handles text extraction from PDF and DOCX files"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        return text
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
        return text
    
    @classmethod
    def extract_text(cls, file_path: str, file_extension: str) -> str:
        """Extract text based on file extension"""
        if file_extension.lower() == '.pdf':
            return cls.extract_text_from_pdf(file_path)
        elif file_extension.lower() == '.docx':
            return cls.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")


class QuizManager:
    """Manages quiz creation, storage, and scoring"""
    
    @staticmethod
    def save_quiz(quiz_data: Dict[str, Any]) -> str:
        """Save quiz to JSON file and return quiz ID"""
        quiz_id = str(uuid.uuid4())
        quiz_data['id'] = quiz_id
        quiz_data['created_at'] = datetime.now().isoformat()
        
        filename = f"data/quiz_{quiz_id}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(quiz_data, f, indent=2, ensure_ascii=False)
        
        return quiz_id
    
    @staticmethod
    def load_quiz(quiz_id: str) -> Dict[str, Any]:
        """Load quiz from JSON file"""
        filename = f"data/quiz_{quiz_id}.json"
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Quiz {quiz_id} not found")
        
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def calculate_score(quiz_data: Dict[str, Any], user_answers: Dict[str, str]) -> Dict[str, Any]:
        """Calculate quiz score and provide feedback"""
        total_questions = len(quiz_data['questions'])
        correct_answers = 0
        detailed_results = []
        
        for i, question in enumerate(quiz_data['questions']):
            question_num = str(i)
            user_answer = user_answers.get(question_num, "")
            correct_answer = question['correct_answer']
            is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
            
            if is_correct:
                correct_answers += 1
            
            detailed_results.append({
                'question': question['question'],
                'your_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'explanation': question.get('explanation', '')
            })
        
        score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        return {
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'score_percentage': round(score_percentage, 2),
            'detailed_results': detailed_results,
            'timestamp': datetime.now().isoformat()
        }


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx'}


@app.route('/')
def index():
    """Main page with upload form"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and text extraction"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF and DOCX files are allowed'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text
        file_extension = os.path.splitext(filename)[1]
        extracted_text = DocumentProcessor.extract_text(file_path, file_extension)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'extracted_text': extracted_text,
            'text_length': len(extracted_text)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/quiz/create', methods=['POST'])
def create_quiz():
    """Create a new quiz from questions and answers"""
    try:
        data = request.get_json()
        
        if not data or 'title' not in data or 'questions' not in data:
            return jsonify({'error': 'Invalid quiz data'}), 400
        
        # Validate questions format
        questions = data['questions']
        if not isinstance(questions, list) or len(questions) == 0:
            return jsonify({'error': 'At least one question is required'}), 400
        
        for i, question in enumerate(questions):
            required_fields = ['question', 'options', 'correct_answer']
            if not all(field in question for field in required_fields):
                return jsonify({'error': f'Question {i+1} is missing required fields'}), 400
        
        # Save quiz
        quiz_id = QuizManager.save_quiz(data)
        
        return jsonify({
            'success': True,
            'quiz_id': quiz_id,
            'message': 'Quiz created successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/quiz/<quiz_id>', methods=['GET'])
def get_quiz(quiz_id: str):
    """Get quiz questions for taking the quiz"""
    try:
        quiz_data = QuizManager.load_quiz(quiz_id)
        
        # Return quiz without correct answers
        quiz_for_user = {
            'id': quiz_data['id'],
            'title': quiz_data['title'],
            'description': quiz_data.get('description', ''),
            'questions': []
        }
        
        for question in quiz_data['questions']:
            quiz_for_user['questions'].append({
                'question': question['question'],
                'options': question['options']
            })
        
        return jsonify(quiz_for_user)
    
    except FileNotFoundError:
        return jsonify({'error': 'Quiz not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/quiz/<quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id: str):
    """Submit quiz answers and get results"""
    try:
        quiz_data = QuizManager.load_quiz(quiz_id)
        user_answers = request.get_json()
        
        if not user_answers or 'answers' not in user_answers:
            return jsonify({'error': 'No answers provided'}), 400
        
        # Calculate score and feedback
        results = QuizManager.calculate_score(quiz_data, user_answers['answers'])
        
        # Store session results
        session_id = str(uuid.uuid4())
        quiz_sessions[session_id] = {
            'quiz_id': quiz_id,
            'results': results,
            'user_info': user_answers.get('user_info', {})
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'results': results
        })
    
    except FileNotFoundError:
        return jsonify({'error': 'Quiz not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/quiz/list', methods=['GET'])
def list_quizzes():
    """List all available quizzes"""
    try:
        quizzes = []
        data_dir = 'data'
        
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.startswith('quiz_') and filename.endswith('.json'):
                    quiz_id = filename[5:-5]  # Remove 'quiz_' prefix and '.json' suffix
                    try:
                        quiz_data = QuizManager.load_quiz(quiz_id)
                        quizzes.append({
                            'id': quiz_data['id'],
                            'title': quiz_data['title'],
                            'description': quiz_data.get('description', ''),
                            'question_count': len(quiz_data['questions']),
                            'created_at': quiz_data.get('created_at', '')
                        })
                    except Exception:
                        continue  # Skip invalid quiz files
        
        return jsonify({'quizzes': quizzes})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/session/<session_id>/results', methods=['GET'])
def get_session_results(session_id: str):
    """Get results for a specific quiz session"""
    if session_id not in quiz_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify(quiz_sessions[session_id])


@app.route('/quiz/<quiz_id>')
def quiz_page(quiz_id: str):
    """Render quiz taking page"""
    return render_template('quiz.html', quiz_id=quiz_id)


@app.route('/results/<session_id>')
def results_page(session_id: str):
    """Render quiz results page"""
    return render_template('results.html', session_id=session_id)


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
