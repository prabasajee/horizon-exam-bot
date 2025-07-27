"""
Real-time Features for Horizon Exam Bot
Live quiz sessions, real-time collaboration, and notifications
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import json
from datetime import datetime
import uuid

class RealTimeManager:
    def __init__(self, socketio):
        self.socketio = socketio
        self.active_sessions = {}
        self.live_quizzes = {}
        
    def setup_events(self):
        """Setup all Socket.IO event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            print(f'Client connected: {request.sid}')
            emit('connected', {'status': 'Connected to Horizon Exam Bot'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print(f'Client disconnected: {request.sid}')
            self.cleanup_user_sessions(request.sid)
        
        @self.socketio.on('join_live_quiz')
        def handle_join_live_quiz(data):
            """Join a live quiz session"""
            quiz_id = data.get('quiz_id')
            user_name = data.get('user_name', 'Anonymous')
            
            if quiz_id not in self.live_quizzes:
                self.live_quizzes[quiz_id] = {
                    'participants': {},
                    'start_time': None,
                    'current_question': 0,
                    'questions': [],
                    'status': 'waiting'
                }
            
            # Add participant
            self.live_quizzes[quiz_id]['participants'][request.sid] = {
                'name': user_name,
                'score': 0,
                'answers': [],
                'joined_at': datetime.now().isoformat()
            }
            
            join_room(f'quiz_{quiz_id}')
            
            # Notify all participants
            emit('participant_joined', {
                'participant': user_name,
                'total_participants': len(self.live_quizzes[quiz_id]['participants'])
            }, room=f'quiz_{quiz_id}')
            
            # Send current quiz state to new participant
            emit('quiz_state', {
                'status': self.live_quizzes[quiz_id]['status'],
                'current_question': self.live_quizzes[quiz_id]['current_question'],
                'participants': len(self.live_quizzes[quiz_id]['participants'])
            })
        
        @self.socketio.on('start_live_quiz')
        def handle_start_live_quiz(data):
            """Start a live quiz session (admin only)"""
            quiz_id = data.get('quiz_id')
            questions = data.get('questions', [])
            
            if quiz_id in self.live_quizzes:
                self.live_quizzes[quiz_id].update({
                    'questions': questions,
                    'status': 'active',
                    'start_time': datetime.now().isoformat(),
                    'current_question': 0
                })
                
                # Notify all participants
                emit('quiz_started', {
                    'message': 'Quiz has started!',
                    'total_questions': len(questions),
                    'first_question': questions[0] if questions else None
                }, room=f'quiz_{quiz_id}')
        
        @self.socketio.on('submit_live_answer')
        def handle_submit_live_answer(data):
            """Handle live quiz answer submission"""
            quiz_id = data.get('quiz_id')
            question_index = data.get('question_index')
            answer = data.get('answer')
            
            if quiz_id in self.live_quizzes and request.sid in self.live_quizzes[quiz_id]['participants']:
                participant = self.live_quizzes[quiz_id]['participants'][request.sid]
                
                # Store answer
                while len(participant['answers']) <= question_index:
                    participant['answers'].append(None)
                
                participant['answers'][question_index] = {
                    'answer': answer,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Calculate score if correct answer is available
                questions = self.live_quizzes[quiz_id]['questions']
                if question_index < len(questions):
                    correct_answer = questions[question_index].get('correct_answer')
                    if answer == correct_answer:
                        participant['score'] += 1
                
                # Notify quiz moderator about submission
                emit('answer_submitted', {
                    'participant': participant['name'],
                    'question_index': question_index,
                    'submitted_count': len([p for p in self.live_quizzes[quiz_id]['participants'].values() 
                                          if len(p['answers']) > question_index and p['answers'][question_index] is not None])
                }, room=f'quiz_{quiz_id}')
        
        @self.socketio.on('next_question')
        def handle_next_question(data):
            """Move to next question in live quiz"""
            quiz_id = data.get('quiz_id')
            
            if quiz_id in self.live_quizzes:
                current_q = self.live_quizzes[quiz_id]['current_question']
                questions = self.live_quizzes[quiz_id]['questions']
                
                if current_q + 1 < len(questions):
                    self.live_quizzes[quiz_id]['current_question'] = current_q + 1
                    
                    emit('next_question', {
                        'question_index': current_q + 1,
                        'question': questions[current_q + 1],
                        'total_questions': len(questions)
                    }, room=f'quiz_{quiz_id}')
                else:
                    # Quiz completed
                    self.live_quizzes[quiz_id]['status'] = 'completed'
                    
                    # Calculate final scores
                    leaderboard = []
                    for sid, participant in self.live_quizzes[quiz_id]['participants'].items():
                        leaderboard.append({
                            'name': participant['name'],
                            'score': participant['score'],
                            'total_questions': len(questions)
                        })
                    
                    leaderboard.sort(key=lambda x: x['score'], reverse=True)
                    
                    emit('quiz_completed', {
                        'message': 'Quiz completed!',
                        'leaderboard': leaderboard
                    }, room=f'quiz_{quiz_id}')
        
        @self.socketio.on('send_chat_message')
        def handle_chat_message(data):
            """Handle chat messages during live quiz"""
            quiz_id = data.get('quiz_id')
            message = data.get('message')
            user_name = data.get('user_name', 'Anonymous')
            
            emit('chat_message', {
                'user': user_name,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }, room=f'quiz_{quiz_id}')
        
        @self.socketio.on('typing')
        def handle_typing(data):
            """Handle typing indicators"""
            room = data.get('room')
            user_name = data.get('user_name')
            
            emit('user_typing', {
                'user': user_name,
                'timestamp': datetime.now().isoformat()
            }, room=room, include_self=False)
        
        @self.socketio.on('request_hint')
        def handle_hint_request(data):
            """Handle hint requests during quiz"""
            quiz_id = data.get('quiz_id')
            question_index = data.get('question_index')
            
            if quiz_id in self.live_quizzes:
                questions = self.live_quizzes[quiz_id]['questions']
                if question_index < len(questions):
                    question = questions[question_index]
                    hint = question.get('hint', 'No hint available for this question.')
                    
                    emit('hint_provided', {
                        'question_index': question_index,
                        'hint': hint
                    })
    
    def cleanup_user_sessions(self, sid):
        """Clean up user data when they disconnect"""
        for quiz_id, quiz_data in self.live_quizzes.items():
            if sid in quiz_data['participants']:
                participant_name = quiz_data['participants'][sid]['name']
                del quiz_data['participants'][sid]
                
                # Notify other participants
                self.socketio.emit('participant_left', {
                    'participant': participant_name,
                    'total_participants': len(quiz_data['participants'])
                }, room=f'quiz_{quiz_id}')
    
    def get_live_quiz_stats(self, quiz_id):
        """Get real-time statistics for a live quiz"""
        if quiz_id not in self.live_quizzes:
            return None
        
        quiz_data = self.live_quizzes[quiz_id]
        
        return {
            'status': quiz_data['status'],
            'participants': len(quiz_data['participants']),
            'current_question': quiz_data['current_question'],
            'total_questions': len(quiz_data['questions']),
            'start_time': quiz_data['start_time'],
            'participant_list': [p['name'] for p in quiz_data['participants'].values()]
        }

# Notification system
class NotificationManager:
    def __init__(self, socketio):
        self.socketio = socketio
    
    def send_notification(self, user_id, notification_type, title, message, data=None):
        """Send real-time notification to specific user"""
        notification = {
            'id': str(uuid.uuid4()),
            'type': notification_type,
            'title': title,
            'message': message,
            'data': data or {},
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        
        self.socketio.emit('notification', notification, room=f'user_{user_id}')
        return notification
    
    def broadcast_notification(self, notification_type, title, message, data=None):
        """Send notification to all connected users"""
        notification = {
            'id': str(uuid.uuid4()),
            'type': notification_type,
            'title': title,
            'message': message,
            'data': data or {},
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        
        self.socketio.emit('broadcast_notification', notification)
        return notification

# Enhanced quiz features
class QuizCollaboration:
    def __init__(self, socketio):
        self.socketio = socketio
        self.collaborative_sessions = {}
    
    def create_collaborative_session(self, session_id, creator_id):
        """Create a new collaborative quiz creation session"""
        self.collaborative_sessions[session_id] = {
            'creator_id': creator_id,
            'participants': {},
            'quiz_data': {
                'title': '',
                'description': '',
                'questions': []
            },
            'created_at': datetime.now().isoformat()
        }
    
    def join_collaborative_session(self, session_id, user_id, username):
        """Join a collaborative quiz creation session"""
        if session_id in self.collaborative_sessions:
            self.collaborative_sessions[session_id]['participants'][user_id] = {
                'username': username,
                'joined_at': datetime.now().isoformat(),
                'socket_id': request.sid
            }
            
            join_room(f'collab_{session_id}')
            
            # Notify other participants
            self.socketio.emit('participant_joined_collaboration', {
                'user': username,
                'participants_count': len(self.collaborative_sessions[session_id]['participants'])
            }, room=f'collab_{session_id}')
            
            return True
        return False
    
    def update_collaborative_quiz(self, session_id, user_id, update_data):
        """Update collaborative quiz data"""
        if session_id in self.collaborative_sessions:
            # Update quiz data
            quiz_data = self.collaborative_sessions[session_id]['quiz_data']
            quiz_data.update(update_data)
            
            # Broadcast changes to all participants
            self.socketio.emit('quiz_updated', {
                'updated_by': self.collaborative_sessions[session_id]['participants'][user_id]['username'],
                'changes': update_data,
                'quiz_data': quiz_data
            }, room=f'collab_{session_id}')
            
            return True
        return False
