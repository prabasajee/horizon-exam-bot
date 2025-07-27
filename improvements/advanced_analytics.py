"""
Advanced Analytics and Reporting System for Horizon Exam Bot
Comprehensive data analysis, insights, and reporting features
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import io
import base64
from flask import Blueprint, jsonify, render_template, request

analytics_bp = Blueprint('analytics', __name__)

class AdvancedAnalytics:
    def __init__(self, db_path='horizon_exam.db'):
        self.db_path = db_path
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_quiz_performance_analytics(self, quiz_id=None, date_range=30):
        """Get comprehensive quiz performance analytics"""
        conn = self.get_connection()
        
        # Base query
        base_query = '''
            SELECT 
                qa.id, qa.quiz_id, qa.score, qa.total_questions, qa.percentage,
                qa.time_taken, qa.completed_at, qa.user_name,
                q.title as quiz_title, q.category, q.difficulty_level
            FROM quiz_attempts qa
            JOIN quizzes q ON qa.quiz_id = q.id
            WHERE qa.completed_at >= datetime('now', '-{} days')
        '''.format(date_range)
        
        if quiz_id:
            base_query += f' AND qa.quiz_id = {quiz_id}'
        
        df = pd.read_sql_query(base_query, conn)
        conn.close()
        
        if df.empty:
            return {
                'total_attempts': 0,
                'average_score': 0,
                'completion_rate': 0,
                'performance_trends': [],
                'score_distribution': {},
                'time_analytics': {}
            }
        
        # Calculate analytics
        analytics = {
            'total_attempts': len(df),
            'average_score': round(df['percentage'].mean(), 2),
            'median_score': round(df['percentage'].median(), 2),
            'highest_score': df['percentage'].max(),
            'lowest_score': df['percentage'].min(),
            'completion_rate': round((len(df) / len(df)) * 100, 2),  # This would need adjustment for started vs completed
            
            # Score distribution
            'score_distribution': {
                'excellent': len(df[df['percentage'] >= 90]),
                'good': len(df[(df['percentage'] >= 75) & (df['percentage'] < 90)]),
                'average': len(df[(df['percentage'] >= 60) & (df['percentage'] < 75)]),
                'poor': len(df[df['percentage'] < 60])
            },
            
            # Time analytics
            'time_analytics': {
                'average_time': round(df['time_taken'].mean() / 60000, 2) if not df['time_taken'].isna().all() else 0,
                'median_time': round(df['time_taken'].median() / 60000, 2) if not df['time_taken'].isna().all() else 0,
                'fastest_completion': round(df['time_taken'].min() / 60000, 2) if not df['time_taken'].isna().all() else 0,
                'slowest_completion': round(df['time_taken'].max() / 60000, 2) if not df['time_taken'].isna().all() else 0
            },
            
            # Daily trends
            'daily_trends': self.calculate_daily_trends(df),
            
            # Question-level analytics
            'question_analytics': self.get_question_level_analytics(quiz_id) if quiz_id else None
        }
        
        return analytics
    
    def calculate_daily_trends(self, df):
        """Calculate daily performance trends"""
        df['date'] = pd.to_datetime(df['completed_at']).dt.date
        daily_stats = df.groupby('date').agg({
            'percentage': ['mean', 'count'],
            'time_taken': 'mean'
        }).round(2)
        
        trends = []
        for date, stats in daily_stats.iterrows():
            trends.append({
                'date': str(date),
                'average_score': stats['percentage']['mean'],
                'attempts': stats['percentage']['count'],
                'average_time': stats['time_taken']['mean'] / 60000 if not pd.isna(stats['time_taken']['mean']) else 0
            })
        
        return trends
    
    def get_question_level_analytics(self, quiz_id):
        """Get detailed analytics for each question in a quiz"""
        conn = self.get_connection()
        
        # Get quiz questions
        questions_query = '''
            SELECT id, question_text, correct_answer, order_index
            FROM questions 
            WHERE quiz_id = ? 
            ORDER BY order_index
        '''
        questions_df = pd.read_sql_query(questions_query, conn, params=(quiz_id,))
        
        # Get attempts with answers
        attempts_query = '''
            SELECT answers_json FROM quiz_attempts 
            WHERE quiz_id = ? AND answers_json IS NOT NULL
        '''
        attempts_df = pd.read_sql_query(attempts_query, conn, params=(quiz_id,))
        conn.close()
        
        question_analytics = []
        
        for _, question in questions_df.iterrows():
            correct_count = 0
            total_count = 0
            answer_distribution = {}
            
            for _, attempt in attempts_df.iterrows():
                try:
                    answers = json.loads(attempt['answers_json'])
                    question_index = str(question['order_index'])
                    
                    if question_index in answers:
                        total_count += 1
                        user_answer = answers[question_index]
                        
                        # Count answer distribution
                        answer_distribution[user_answer] = answer_distribution.get(user_answer, 0) + 1
                        
                        # Count correct answers
                        if user_answer == question['correct_answer']:
                            correct_count += 1
                except:
                    continue
            
            difficulty_score = (correct_count / total_count * 100) if total_count > 0 else 0
            
            question_analytics.append({
                'question_id': question['id'],
                'question_text': question['question_text'][:100] + '...' if len(question['question_text']) > 100 else question['question_text'],
                'correct_percentage': round(difficulty_score, 2),
                'total_attempts': total_count,
                'correct_attempts': correct_count,
                'difficulty_level': self.categorize_difficulty(difficulty_score),
                'answer_distribution': answer_distribution
            })
        
        return question_analytics
    
    def categorize_difficulty(self, correct_percentage):
        """Categorize question difficulty based on correct percentage"""
        if correct_percentage >= 80:
            return 'Easy'
        elif correct_percentage >= 60:
            return 'Medium'
        elif correct_percentage >= 40:
            return 'Hard'
        else:
            return 'Very Hard'
    
    def get_user_analytics(self, user_id=None, date_range=30):
        """Get user performance analytics"""
        conn = self.get_connection()
        
        query = '''
            SELECT 
                qa.user_id, qa.score, qa.total_questions, qa.percentage,
                qa.time_taken, qa.completed_at, qa.user_name,
                q.title as quiz_title, q.category
            FROM quiz_attempts qa
            JOIN quizzes q ON qa.quiz_id = q.id
            WHERE qa.completed_at >= datetime('now', '-{} days')
        '''.format(date_range)
        
        if user_id:
            query += f' AND qa.user_id = {user_id}'
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return {'message': 'No data available'}
        
        # User-specific analytics
        if user_id:
            user_df = df[df['user_id'] == user_id]
            return {
                'total_quizzes': len(user_df),
                'average_score': round(user_df['percentage'].mean(), 2),
                'best_score': user_df['percentage'].max(),
                'improvement_trend': self.calculate_improvement_trend(user_df),
                'category_performance': self.get_category_performance(user_df),
                'recent_activity': user_df.tail(10).to_dict('records')
            }
        
        # Overall user analytics
        user_stats = df.groupby('user_id').agg({
            'percentage': ['mean', 'count', 'max'],
            'time_taken': 'mean'
        }).round(2)
        
        top_performers = user_stats.sort_values(('percentage', 'mean'), ascending=False).head(10)
        
        return {
            'total_users': len(user_stats),
            'top_performers': top_performers.to_dict('records'),
            'average_user_score': round(user_stats[('percentage', 'mean')].mean(), 2),
            'user_engagement': {
                'active_users': len(df[df['completed_at'] >= (datetime.now() - timedelta(days=7)).isoformat()]),
                'returning_users': len(user_stats[user_stats[('percentage', 'count')] > 1])
            }
        }
    
    def calculate_improvement_trend(self, user_df):
        """Calculate user improvement trend over time"""
        user_df_sorted = user_df.sort_values('completed_at')
        scores = user_df_sorted['percentage'].tolist()
        
        if len(scores) < 2:
            return 'Insufficient data'
        
        # Simple linear trend
        recent_scores = scores[-5:]  # Last 5 attempts
        early_scores = scores[:5]   # First 5 attempts
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        early_avg = sum(early_scores) / len(early_scores)
        
        improvement = recent_avg - early_avg
        
        if improvement > 10:
            return 'Strong Improvement'
        elif improvement > 5:
            return 'Moderate Improvement'
        elif improvement > -5:
            return 'Stable'
        else:
            return 'Declining'
    
    def get_category_performance(self, user_df):
        """Get user performance by quiz category"""
        category_stats = user_df.groupby('category').agg({
            'percentage': ['mean', 'count']
        }).round(2)
        
        performance = []
        for category, stats in category_stats.iterrows():
            performance.append({
                'category': category,
                'average_score': stats['percentage']['mean'],
                'attempts': stats['percentage']['count']
            })
        
        return performance
    
    def generate_performance_chart(self, data, chart_type='line'):
        """Generate performance visualization charts"""
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if chart_type == 'line':
            dates = [item['date'] for item in data['daily_trends']]
            scores = [item['average_score'] for item in data['daily_trends']]
            
            ax.plot(dates, scores, marker='o', linewidth=2, markersize=6)
            ax.set_title('Performance Trend Over Time')
            ax.set_xlabel('Date')
            ax.set_ylabel('Average Score (%)')
            plt.xticks(rotation=45)
            
        elif chart_type == 'bar':
            categories = list(data['score_distribution'].keys())
            values = list(data['score_distribution'].values())
            
            colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
            ax.bar(categories, values, color=colors)
            ax.set_title('Score Distribution')
            ax.set_ylabel('Number of Attempts')
        
        plt.tight_layout()
        
        # Convert to base64 string
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        
        chart_data = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{chart_data}"
    
    def export_analytics_report(self, quiz_id=None, format='json'):
        """Export comprehensive analytics report"""
        analytics_data = {
            'generated_at': datetime.now().isoformat(),
            'quiz_analytics': self.get_quiz_performance_analytics(quiz_id),
            'user_analytics': self.get_user_analytics(),
            'summary': {
                'total_quizzes': self.get_total_quizzes(),
                'total_attempts': self.get_total_attempts(),
                'platform_growth': self.get_platform_growth_metrics()
            }
        }
        
        if format == 'json':
            return analytics_data
        elif format == 'csv':
            # Convert to CSV format
            return self.convert_to_csv(analytics_data)
        
        return analytics_data
    
    def get_total_quizzes(self):
        """Get total number of quizzes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM quizzes WHERE is_active = 1')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_total_attempts(self):
        """Get total number of quiz attempts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM quiz_attempts')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_platform_growth_metrics(self):
        """Get platform growth and engagement metrics"""
        conn = self.get_connection()
        
        # Monthly growth
        monthly_query = '''
            SELECT 
                strftime('%Y-%m', completed_at) as month,
                COUNT(*) as attempts,
                COUNT(DISTINCT user_id) as unique_users
            FROM quiz_attempts
            WHERE completed_at >= datetime('now', '-12 months')
            GROUP BY strftime('%Y-%m', completed_at)
            ORDER BY month
        '''
        
        monthly_df = pd.read_sql_query(monthly_query, conn)
        conn.close()
        
        return {
            'monthly_growth': monthly_df.to_dict('records'),
            'growth_rate': self.calculate_growth_rate(monthly_df),
            'user_retention': self.calculate_user_retention()
        }
    
    def calculate_growth_rate(self, monthly_df):
        """Calculate month-over-month growth rate"""
        if len(monthly_df) < 2:
            return 0
        
        current_month = monthly_df.iloc[-1]['attempts']
        previous_month = monthly_df.iloc[-2]['attempts']
        
        if previous_month == 0:
            return 100 if current_month > 0 else 0
        
        growth_rate = ((current_month - previous_month) / previous_month) * 100
        return round(growth_rate, 2)
    
    def calculate_user_retention(self):
        """Calculate user retention rate"""
        conn = self.get_connection()
        
        # Users who took quizzes this month and last month
        retention_query = '''
            WITH this_month AS (
                SELECT DISTINCT user_id 
                FROM quiz_attempts 
                WHERE completed_at >= datetime('now', 'start of month')
            ),
            last_month AS (
                SELECT DISTINCT user_id 
                FROM quiz_attempts 
                WHERE completed_at >= datetime('now', '-1 month', 'start of month')
                AND completed_at < datetime('now', 'start of month')
            )
            SELECT 
                (SELECT COUNT(*) FROM this_month) as current_users,
                (SELECT COUNT(*) FROM last_month) as previous_users,
                (SELECT COUNT(*) FROM this_month WHERE user_id IN (SELECT user_id FROM last_month)) as retained_users
        '''
        
        cursor = conn.cursor()
        cursor.execute(retention_query)
        result = cursor.fetchone()
        conn.close()
        
        if result['previous_users'] > 0:
            retention_rate = (result['retained_users'] / result['previous_users']) * 100
            return round(retention_rate, 2)
        
        return 0

# Flask routes for analytics
@analytics_bp.route('/api/analytics/dashboard')
def analytics_dashboard():
    """Get dashboard analytics data"""
    analytics = AdvancedAnalytics()
    
    try:
        dashboard_data = {
            'quiz_analytics': analytics.get_quiz_performance_analytics(),
            'user_analytics': analytics.get_user_analytics(),
            'platform_metrics': analytics.get_platform_growth_metrics()
        }
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics')
def analytics_page():
    """Render analytics dashboard page"""
    return render_template('analytics/dashboard.html')

@analytics_bp.route('/api/analytics/quiz/<int:quiz_id>')
def quiz_specific_analytics(quiz_id):
    """Get analytics for a specific quiz"""
    analytics = AdvancedAnalytics()
    
    try:
        quiz_data = analytics.get_quiz_performance_analytics(quiz_id)
        
        return jsonify({
            'success': True,
            'data': quiz_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/api/analytics/export')
def export_analytics():
    """Export analytics report"""
    analytics = AdvancedAnalytics()
    format_type = request.args.get('format', 'json')
    quiz_id = request.args.get('quiz_id', type=int)
    
    try:
        report_data = analytics.export_analytics_report(quiz_id, format_type)
        
        return jsonify({
            'success': True,
            'data': report_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
