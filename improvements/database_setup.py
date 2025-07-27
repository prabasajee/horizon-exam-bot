"""
Database setup and migration script for Horizon Exam Bot
This will upgrade from JSON storage to SQLite database
"""

import sqlite3
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

class DatabaseSetup:
    def __init__(self, db_path='horizon_exam.db'):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Connect to SQLite database"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def create_tables(self):
        """Create all necessary tables"""
        cursor = self.connection.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                role VARCHAR(20) DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Quizzes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                creator_id INTEGER,
                category VARCHAR(100),
                difficulty_level VARCHAR(20) DEFAULT 'medium',
                time_limit INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (creator_id) REFERENCES users(id)
            )
        ''')
        
        # Questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                question_type VARCHAR(20) DEFAULT 'multiple_choice',
                option_a VARCHAR(500),
                option_b VARCHAR(500),
                option_c VARCHAR(500),
                option_d VARCHAR(500),
                correct_answer CHAR(1) NOT NULL,
                explanation TEXT,
                points INTEGER DEFAULT 1,
                order_index INTEGER,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
            )
        ''')
        
        # Quiz attempts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                quiz_id INTEGER NOT NULL,
                user_name VARCHAR(100),
                user_email VARCHAR(100),
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                percentage DECIMAL(5,2),
                time_taken INTEGER,
                started_at TIMESTAMP,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                answers_json TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
            )
        ''')
        
        # Notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                source_content TEXT,
                note_style VARCHAR(50) DEFAULT 'bullet',
                tags VARCHAR(500),
                is_favorite BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                quiz_attempts INTEGER DEFAULT 0,
                quizzes_created INTEGER DEFAULT 0,
                notes_generated INTEGER DEFAULT 0,
                active_users INTEGER DEFAULT 0,
                avg_score DECIMAL(5,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.connection.commit()
        print("✅ Database tables created successfully!")
    
    def migrate_existing_data(self):
        """Migrate data from JSON files to database"""
        cursor = self.connection.cursor()
        
        # Create default admin user
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, email, password_hash, role, first_name, last_name)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@horizon.com', admin_password, 'admin', 'System', 'Administrator'))
        
        admin_id = cursor.lastrowid or 1
        
        # Migrate quizzes from JSON files
        data_dir = 'data'
        if os.path.exists(data_dir):
            migrated_quizzes = 0
            migrated_notes = 0
            
            for filename in os.listdir(data_dir):
                if filename.startswith('quiz_') and filename.endswith('.json'):
                    try:
                        with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                            quiz_data = json.load(f)
                        
                        # Insert quiz
                        cursor.execute('''
                            INSERT INTO quizzes (title, description, creator_id, created_at)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            quiz_data.get('title', 'Imported Quiz'),
                            quiz_data.get('description', ''),
                            admin_id,
                            quiz_data.get('created_at', datetime.now().isoformat())
                        ))
                        
                        quiz_id = cursor.lastrowid
                        
                        # Insert questions
                        for i, question in enumerate(quiz_data.get('questions', [])):
                            cursor.execute('''
                                INSERT INTO questions (
                                    quiz_id, question_text, option_a, option_b, 
                                    option_c, option_d, correct_answer, explanation, order_index
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                quiz_id,
                                question.get('question', ''),
                                question.get('options', {}).get('A', ''),
                                question.get('options', {}).get('B', ''),
                                question.get('options', {}).get('C', ''),
                                question.get('options', {}).get('D', ''),
                                question.get('correct_answer', 'A'),
                                question.get('explanation', ''),
                                i
                            ))
                        
                        migrated_quizzes += 1
                        
                    except Exception as e:
                        print(f"❌ Error migrating quiz {filename}: {e}")
                
                elif filename.startswith('notes_') and filename.endswith('.json'):
                    try:
                        with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                            notes_data = json.load(f)
                        
                        cursor.execute('''
                            INSERT INTO notes (title, content, source_content, created_at)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            notes_data.get('title', 'Imported Note'),
                            notes_data.get('content', ''),
                            notes_data.get('source_content', ''),
                            notes_data.get('created_at', datetime.now().isoformat())
                        ))
                        
                        migrated_notes += 1
                        
                    except Exception as e:
                        print(f"❌ Error migrating note {filename}: {e}")
            
            self.connection.commit()
            print(f"✅ Migrated {migrated_quizzes} quizzes and {migrated_notes} notes!")
    
    def create_indexes(self):
        """Create database indexes for better performance"""
        cursor = self.connection.cursor()
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_quiz_attempts_user_id ON quiz_attempts(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_quiz_attempts_quiz_id ON quiz_attempts(quiz_id)", 
            "CREATE INDEX IF NOT EXISTS idx_quiz_attempts_completed_at ON quiz_attempts(completed_at)",
            "CREATE INDEX IF NOT EXISTS idx_questions_quiz_id ON questions(quiz_id)",
            "CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_quizzes_creator_id ON quizzes(creator_id)",
            "CREATE INDEX IF NOT EXISTS idx_quizzes_created_at ON quizzes(created_at)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        self.connection.commit()
        print("✅ Database indexes created!")
    
    def setup_database(self):
        """Complete database setup process"""
        try:
            self.connect()
            print("🔄 Setting up database...")
            
            self.create_tables()
            self.migrate_existing_data()
            self.create_indexes()
            
            print("✅ Database setup completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            return False
        finally:
            if self.connection:
                self.connection.close()

if __name__ == "__main__":
    db_setup = DatabaseSetup()
    db_setup.setup_database()
