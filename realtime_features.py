"""
Real-time Features with WebSocket Support
Enables live quiz sessions, real-time analytics, and collaborative features
"""
from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from datetime import datetime
import json
import uuid

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store for active quiz sessions
active_sessions = {}
user_sessions = {}

class LiveQuizSession:
    """Manages live quiz sessions with real-time features"""
    
    def __init__(self, quiz_id, host_id):
        self.quiz_id = quiz_id
        self.host_id = host_id
        self.session_id = str(uuid.uuid4())
        self.participants = {}
        self.current_question = 0
        self.status = 'waiting'  # waiting, active, paused, completed
        self.created_at = datetime.utcnow()
        self.settings = {
            'time_per_question': 30,  # seconds
            'show_live_results': True,
            'allow_late_joins': True
        }
    
    def add_participant(self, user_id, username, socket_id):
        """Add a participant to the session"""
        self.participants[user_id] = {
            'username': username,
            'socket_id': socket_id,
            'joined_at': datetime.utcnow(),
            'score': 0,
            'answers': {}
        }
    
    def remove_participant(self, user_id):
        """Remove a participant from the session"""
        if user_id in self.participants:
            del self.participants[user_id]
    
    def get_leaderboard(self):
        """Get current leaderboard"""
        participants = list(self.participants.values())
        participants.sort(key=lambda x: x['score'], reverse=True)
        return participants[:10]

@socketio.on('connect')
def handle_connect():
    """Handle new WebSocket connection"""
    print(f'User connected: {request.sid}')
    emit('connected', {'status': 'success', 'message': 'Connected to Horizon Exam Bot'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    session_id = user_sessions.get(request.sid)
    if session_id and session_id in active_sessions:
        session = active_sessions[session_id]
        # Remove user from session
        user_id = None
        for uid, participant in session.participants.items():
            if participant['socket_id'] == request.sid:
                user_id = uid
                break
        
        if user_id:
            session.remove_participant(user_id)
            # Notify other participants
            emit('participant_left', {
                'user_id': user_id,
                'participant_count': len(session.participants)
            }, room=session_id, include_self=False)
    
    if request.sid in user_sessions:
        del user_sessions[request.sid]
    
    print(f'User disconnected: {request.sid}')

@socketio.on('create_live_session')
def handle_create_live_session(data):
    """Create a new live quiz session"""
    quiz_id = data.get('quiz_id')
    host_id = data.get('host_id')
    username = data.get('username', 'Host')
    
    # Create new session
    session = LiveQuizSession(quiz_id, host_id)
    active_sessions[session.session_id] = session
    user_sessions[request.sid] = session.session_id
    
    # Add host as participant
    session.add_participant(host_id, username, request.sid)
    
    # Join socket room
    join_room(session.session_id)
    
    emit('session_created', {
        'session_id': session.session_id,
        'quiz_id': quiz_id,
        'status': session.status,
        'settings': session.settings
    })

@socketio.on('join_live_session')
def handle_join_live_session(data):
    """Join an existing live quiz session"""
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    username = data.get('username')
    
    if session_id not in active_sessions:
        emit('join_error', {'message': 'Session not found'})
        return
    
    session = active_sessions[session_id]
    
    # Check if late joins are allowed
    if session.status == 'active' and not session.settings['allow_late_joins']:
        emit('join_error', {'message': 'Session already started and late joins are not allowed'})
        return
    
    # Add participant
    session.add_participant(user_id, username, request.sid)
    user_sessions[request.sid] = session_id
    
    # Join socket room
    join_room(session_id)
    
    # Notify all participants
    emit('participant_joined', {
        'user_id': user_id,
        'username': username,
        'participant_count': len(session.participants)
    }, room=session_id)
    
    # Send session info to new participant
    emit('session_joined', {
        'session_id': session_id,
        'quiz_id': session.quiz_id,
        'status': session.status,
        'current_question': session.current_question,
        'participants': list(session.participants.keys()),
        'participant_count': len(session.participants)
    })

@socketio.on('start_quiz')
def handle_start_quiz(data):
    """Start the live quiz session"""
    session_id = data.get('session_id')
    
    if session_id not in active_sessions:
        emit('error', {'message': 'Session not found'})
        return
    
    session = active_sessions[session_id]
    
    # Only host can start the quiz
    if session.host_id != data.get('user_id'):
        emit('error', {'message': 'Only the host can start the quiz'})
        return
    
    session.status = 'active'
    session.current_question = 1
    
    # Notify all participants
    emit('quiz_started', {
        'session_id': session_id,
        'current_question': session.current_question,
        'time_per_question': session.settings['time_per_question']
    }, room=session_id)

@socketio.on('submit_answer')
def handle_submit_answer(data):
    """Handle answer submission in live quiz"""
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    question_number = data.get('question_number')
    answer = data.get('answer')
    time_taken = data.get('time_taken', 0)
    
    if session_id not in active_sessions:
        emit('error', {'message': 'Session not found'})
        return
    
    session = active_sessions[session_id]
    
    if user_id not in session.participants:
        emit('error', {'message': 'User not in session'})
        return
    
    # Store answer
    participant = session.participants[user_id]
    participant['answers'][question_number] = {
        'answer': answer,
        'time_taken': time_taken,
        'submitted_at': datetime.utcnow()
    }
    
    # Update score (this would normally check against correct answer)
    # For demo purposes, we'll assume random scoring
    import random
    if random.random() > 0.3:  # 70% chance of correct answer
        participant['score'] += 10
    
    # Notify participant
    emit('answer_submitted', {
        'question_number': question_number,
        'status': 'success'
    })
    
    # If showing live results, broadcast to all
    if session.settings['show_live_results']:
        emit('live_results_update', {
            'question_number': question_number,
            'answers_submitted': len([p for p in session.participants.values() 
                                    if question_number in p['answers']]),
            'total_participants': len(session.participants),
            'leaderboard': session.get_leaderboard()[:5]  # Top 5
        }, room=session_id)

@socketio.on('next_question')
def handle_next_question(data):
    """Move to next question"""
    session_id = data.get('session_id')
    
    if session_id not in active_sessions:
        emit('error', {'message': 'Session not found'})
        return
    
    session = active_sessions[session_id]
    
    # Only host can control questions
    if session.host_id != data.get('user_id'):
        emit('error', {'message': 'Only the host can control the quiz'})
        return
    
    session.current_question += 1
    
    # Check if quiz is completed
    total_questions = data.get('total_questions', 10)
    if session.current_question > total_questions:
        session.status = 'completed'
        emit('quiz_completed', {
            'final_leaderboard': session.get_leaderboard(),
            'session_stats': {
                'total_participants': len(session.participants),
                'total_questions': total_questions,
                'session_duration': (datetime.utcnow() - session.created_at).seconds
            }
        }, room=session_id)
    else:
        emit('next_question', {
            'question_number': session.current_question,
            'time_per_question': session.settings['time_per_question']
        }, room=session_id)

@socketio.on('get_live_analytics')
def handle_get_live_analytics(data):
    """Get real-time analytics for the session"""
    session_id = data.get('session_id')
    
    if session_id not in active_sessions:
        emit('error', {'message': 'Session not found'})
        return
    
    session = active_sessions[session_id]
    
    # Calculate analytics
    total_answers = sum(len(p['answers']) for p in session.participants.values())
    avg_score = sum(p['score'] for p in session.participants.values()) / len(session.participants) if session.participants else 0
    
    analytics = {
        'participant_count': len(session.participants),
        'total_answers_submitted': total_answers,
        'average_score': avg_score,
        'current_question': session.current_question,
        'session_duration': (datetime.utcnow() - session.created_at).seconds,
        'leaderboard': session.get_leaderboard(),
        'question_analytics': {}
    }
    
    # Per-question analytics
    for q_num in range(1, session.current_question + 1):
        question_answers = [p['answers'].get(q_num) for p in session.participants.values() if q_num in p['answers']]
        if question_answers:
            avg_time = sum(ans['time_taken'] for ans in question_answers) / len(question_answers)
            analytics['question_analytics'][q_num] = {
                'responses': len(question_answers),
                'avg_time': avg_time,
                'response_rate': len(question_answers) / len(session.participants) * 100
            }
    
    emit('live_analytics', analytics)

@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle chat messages in live session"""
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    message = data.get('message')
    
    if session_id not in active_sessions:
        emit('error', {'message': 'Session not found'})
        return
    
    session = active_sessions[session_id]
    
    if user_id not in session.participants:
        emit('error', {'message': 'User not in session'})
        return
    
    username = session.participants[user_id]['username']
    
    # Broadcast message to all participants
    emit('chat_message', {
        'user_id': user_id,
        'username': username,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }, room=session_id)

# Cleanup inactive sessions periodically
def cleanup_sessions():
    """Remove inactive sessions"""
    current_time = datetime.utcnow()
    to_remove = []
    
    for session_id, session in active_sessions.items():
        # Remove sessions older than 2 hours
        if (current_time - session.created_at).seconds > 7200:
            to_remove.append(session_id)
    
    for session_id in to_remove:
        del active_sessions[session_id]

if __name__ == '__main__':
    socketio.run(app, debug=True)
