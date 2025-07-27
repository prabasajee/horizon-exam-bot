# 📚 Horizon Exam Bot

A Flask-based web application that allows users to upload PDF or DOCX lecture notes, extract text content, create interactive quizzes, and take assessments with detailed feedback and scoring.

## ✨ Features

### 📄 Document Processing
- **Multi-format Support**: Upload PDF and DOCX files
- **Text Extraction**: Automatically extracts text content from uploaded documents
- **File Validation**: Secure file handling with type and size validation
- **Preview**: Display extracted text before quiz creation

### 🎯 Quiz Management
- **Interactive Creation**: Create multiple-choice questions with 4 options
- **Question Types**: Support for text-based questions with explanations
- **Flexible Storage**: Save quizzes as JSON files for easy management
- **Quiz Listing**: View all available quizzes with metadata

### 📝 Quiz Taking Experience
- **Responsive Design**: Mobile-friendly interface
- **Progress Tracking**: Real-time progress bar and question counter
- **Timer**: Track time spent on quiz
- **User Information**: Optional student details collection
- **Navigation**: Smooth user experience with validation

### 📊 Results & Analytics
- **Detailed Scoring**: Comprehensive scoring with percentage and statistics
- **Question-by-Question Review**: See correct/incorrect answers with explanations
- **Performance Analysis**: Personalized feedback and improvement recommendations
- **Printable Results**: Generate PDF-ready result summaries
- **Session Management**: Unique session IDs for result tracking

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/horizon-exam-bot.git
   cd horizon-exam-bot
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your web browser and navigate to `http://localhost:5000`

## 📁 Project Structure

```
horizon-exam-bot/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── index.html        # Home page with upload and quiz creation
│   ├── quiz.html         # Quiz taking interface
│   └── results.html      # Results display page
├── uploads/              # Temporary file uploads (auto-created)
├── data/                 # Quiz storage (auto-created)
│   └── quiz_*.json       # Individual quiz files
└── static/ (optional)    # Static assets (CSS, JS, images)
```

## 🔧 API Endpoints

### File Upload & Processing
- `POST /api/upload` - Upload and extract text from PDF/DOCX files

### Quiz Management
- `POST /api/quiz/create` - Create a new quiz
- `GET /api/quiz/<quiz_id>` - Get quiz questions for taking
- `GET /api/quiz/list` - List all available quizzes

### Quiz Taking & Results
- `POST /api/quiz/<quiz_id>/submit` - Submit quiz answers
- `GET /api/session/<session_id>/results` - Get detailed results

### Web Pages
- `GET /` - Main application page
- `GET /quiz/<quiz_id>` - Quiz taking page
- `GET /results/<session_id>` - Results display page

## 📋 Usage Guide

### 1. Upload Documents
1. Visit the home page
2. Click on the upload area or drag and drop a PDF/DOCX file
3. Wait for text extraction to complete
4. Review the extracted text

### 2. Create Quizzes
1. After uploading a document, scroll to the quiz creation section
2. Enter a quiz title and optional description
3. Add questions using the "Add Question" button
4. For each question:
   - Enter the question text
   - Add four multiple-choice options (A, B, C, D)
   - Select the correct answer
   - Optionally add an explanation
5. Click "Create Quiz" to save

### 3. Take Quizzes
1. From the home page, click "Take Quiz" on any available quiz
2. Answer all questions by selecting the appropriate options
3. Optionally enter your name and email
4. Click "Submit Quiz" when complete

### 4. View Results
1. After submitting a quiz, you'll be redirected to the results page
2. View your score, detailed question review, and performance analysis
3. Print or save results using the print button

## 🛠️ Configuration

### Environment Variables
You can set the following environment variables to customize the application:

```bash
FLASK_ENV=development          # Set to 'production' for production
FLASK_DEBUG=True              # Enable debug mode
SECRET_KEY=your-secret-key    # Set a secure secret key for production
UPLOAD_FOLDER=uploads         # Custom upload directory
MAX_CONTENT_LENGTH=16777216   # Max file size (16MB default)
```

### File Size Limits
The default maximum file size is 16MB. To change this, modify the `MAX_CONTENT_LENGTH` configuration in `app.py`:

```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

## 🔒 Security Features

- **File Type Validation**: Only allows PDF and DOCX files
- **Secure Filename Handling**: Uses Werkzeug's secure_filename
- **File Size Limits**: Prevents oversized file uploads
- **Temporary File Cleanup**: Automatically removes uploaded files after processing
- **Input Validation**: Validates all form inputs and API requests

## 🏗️ Architecture & Design

### Modular Design
The application is designed with modularity in mind:

- **DocumentProcessor**: Handles text extraction from various file formats
- **QuizManager**: Manages quiz creation, storage, and scoring
- **Extensible Design**: Easy to add new file types or question formats

### Data Storage
- **JSON-based**: Quizzes stored as JSON files for simplicity
- **Session Management**: In-memory session storage (easily replaceable with database)
- **Scalable**: Can be extended to use databases like PostgreSQL or MongoDB

### Frontend Architecture
- **Bootstrap 5**: Responsive, modern UI framework
- **Vanilla JavaScript**: No complex frameworks for better performance
- **Progressive Enhancement**: Works without JavaScript for basic functionality

## 🚀 Deployment

### Production Deployment

1. **Set production environment**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-secure-secret-key
   ```

2. **Use a production WSGI server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Configure reverse proxy (Nginx example)**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🔄 Future Enhancements

### Planned Features
- [ ] **Database Integration**: PostgreSQL/MongoDB support
- [ ] **User Authentication**: Login system with user accounts
- [ ] **Advanced Question Types**: True/false, fill-in-the-blank, essay questions
- [ ] **Image Support**: Questions and answers with images
- [ ] **Analytics Dashboard**: Detailed analytics for educators
- [ ] **Bulk Quiz Import**: Import questions from CSV/Excel
- [ ] **Quiz Categories**: Organize quizzes by subject/topic
- [ ] **Collaborative Features**: Share quizzes between users
- [ ] **Mobile App**: Native mobile applications
- [ ] **AI Integration**: Auto-generate questions from text

### Technical Improvements
- [ ] **Caching**: Redis for improved performance
- [ ] **Background Tasks**: Celery for long-running processes
- [ ] **API Rate Limiting**: Prevent abuse
- [ ] **Advanced Security**: OAuth, JWT tokens
- [ ] **Monitoring**: Application performance monitoring
- [ ] **Backup System**: Automated quiz backup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Bug Reports & Feature Requests

Please use the [GitHub Issues](https://github.com/yourusername/horizon-exam-bot/issues) page to report bugs or request features.

## 👥 Support

For support and questions:
- Create an issue on GitHub
- Email: support@horizonexambot.com
- Documentation: [Wiki](https://github.com/yourusername/horizon-exam-bot/wiki)

## 🙏 Acknowledgments

- Flask framework and community
- Bootstrap for the responsive UI
- PyPDF2 and python-docx for document processing
- All contributors and users of this project

---

**Happy Learning! 📚✨**
