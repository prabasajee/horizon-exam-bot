"""
AI-Powered Question Generation Module
Automatically generates quiz questions from extracted text
"""
import re
import random
from typing import List, Dict, Any
import nltk
from textstat import flesch_reading_ease
from collections import Counter

class AIQuestionGenerator:
    """Generates quiz questions using NLP and pattern matching"""
    
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
    
    def generate_questions(self, text: str, num_questions: int = 5) -> List[Dict[str, Any]]:
        """Generate multiple choice questions from text"""
        sentences = nltk.sent_tokenize(text)
        questions = []
        
        # Different question types
        question_generators = [
            self._generate_definition_questions,
            self._generate_factual_questions,
            self._generate_concept_questions,
            self._generate_comparison_questions
        ]
        
        for i in range(num_questions):
            generator = random.choice(question_generators)
            question = generator(sentences)
            if question:
                questions.append(question)
        
        return questions
    
    def _generate_definition_questions(self, sentences: List[str]) -> Dict[str, Any]:
        """Generate definition-based questions"""
        # Look for sentences with 'is', 'are', 'defined as', etc.
        definition_patterns = [
            r'(.+?) is (.+?)\.?$',
            r'(.+?) are (.+?)\.?$',
            r'(.+?) means (.+?)\.?$',
            r'(.+?) refers to (.+?)\.?$'
        ]
        
        for sentence in sentences:
            for pattern in definition_patterns:
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    term = match.group(1).strip()
                    definition = match.group(2).strip()
                    
                    # Generate question
                    question_text = f"What is {term}?"
                    correct_answer = definition
                    
                    # Generate distractors
                    distractors = self._generate_distractors(definition, sentences)
                    
                    return {
                        'question': question_text,
                        'options': {
                            'A': correct_answer,
                            'B': distractors[0] if len(distractors) > 0 else "Alternative definition 1",
                            'C': distractors[1] if len(distractors) > 1 else "Alternative definition 2",
                            'D': distractors[2] if len(distractors) > 2 else "Alternative definition 3"
                        },
                        'correct_answer': 'A',
                        'explanation': f"{term} is correctly defined as {definition}"
                    }
        
        return None
    
    def _generate_factual_questions(self, sentences: List[str]) -> Dict[str, Any]:
        """Generate factual questions"""
        # Look for sentences with numbers, dates, names
        factual_patterns = [
            r'(\d+)',  # Numbers
            r'(\d{4})',  # Years
            r'([A-Z][a-z]+ [A-Z][a-z]+)',  # Proper names
        ]
        
        for sentence in sentences:
            for pattern in factual_patterns:
                matches = re.findall(pattern, sentence)
                if matches:
                    fact = matches[0]
                    # Create question by replacing the fact with a blank
                    question_text = sentence.replace(fact, "____") + "?"
                    
                    # Generate distractors
                    if pattern == r'(\d+)':
                        distractors = [str(int(fact) + random.randint(1, 10)) for _ in range(3)]
                    elif pattern == r'(\d{4})':
                        year = int(fact)
                        distractors = [str(year + random.randint(-10, 10)) for _ in range(3)]
                    else:
                        distractors = ["Alternative name 1", "Alternative name 2", "Alternative name 3"]
                    
                    return {
                        'question': question_text,
                        'options': {
                            'A': fact,
                            'B': distractors[0],
                            'C': distractors[1],
                            'D': distractors[2]
                        },
                        'correct_answer': 'A',
                        'explanation': f"The correct answer is {fact} as stated in the text."
                    }
        
        return None
    
    def _generate_concept_questions(self, sentences: List[str]) -> Dict[str, Any]:
        """Generate conceptual understanding questions"""
        # Look for cause-effect relationships
        concept_patterns = [
            r'(.+?) because (.+?)\.?$',
            r'(.+?) results in (.+?)\.?$',
            r'(.+?) leads to (.+?)\.?$',
            r'(.+?) causes (.+?)\.?$'
        ]
        
        for sentence in sentences:
            for pattern in concept_patterns:
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    cause = match.group(2).strip()
                    effect = match.group(1).strip()
                    
                    question_text = f"What causes {effect}?"
                    correct_answer = cause
                    
                    distractors = self._generate_concept_distractors(cause)
                    
                    return {
                        'question': question_text,
                        'options': {
                            'A': correct_answer,
                            'B': distractors[0],
                            'C': distractors[1],
                            'D': distractors[2]
                        },
                        'correct_answer': 'A',
                        'explanation': f"{effect} is caused by {cause}."
                    }
        
        return None
    
    def _generate_comparison_questions(self, sentences: List[str]) -> Dict[str, Any]:
        """Generate comparison questions"""
        comparison_words = ['unlike', 'compared to', 'whereas', 'while', 'different from']
        
        for sentence in sentences:
            if any(word in sentence.lower() for word in comparison_words):
                # Extract key concepts
                words = nltk.word_tokenize(sentence)
                pos_tags = nltk.pos_tag(words)
                
                # Find nouns (potential concepts to compare)
                nouns = [word for word, pos in pos_tags if pos.startswith('NN')]
                
                if len(nouns) >= 2:
                    concept1, concept2 = random.sample(nouns, 2)
                    
                    question_text = f"How does {concept1} differ from {concept2}?"
                    correct_answer = "Based on the context provided in the text"
                    
                    distractors = [
                        "They are identical in all aspects",
                        "There is no significant difference",
                        "The text does not provide this information"
                    ]
                    
                    return {
                        'question': question_text,
                        'options': {
                            'A': correct_answer,
                            'B': distractors[0],
                            'C': distractors[1],
                            'D': distractors[2]
                        },
                        'correct_answer': 'A',
                        'explanation': f"The text provides context about the differences between {concept1} and {concept2}."
                    }
        
        return None
    
    def _generate_distractors(self, correct_answer: str, sentences: List[str]) -> List[str]:
        """Generate plausible wrong answers"""
        distractors = []
        
        # Method 1: Use similar sentences
        for sentence in sentences:
            if correct_answer.lower() not in sentence.lower() and len(sentence) < 100:
                distractors.append(sentence.strip())
                if len(distractors) >= 3:
                    break
        
        # Method 2: Generate generic distractors if not enough found
        while len(distractors) < 3:
            distractors.append(f"Alternative answer {len(distractors) + 1}")
        
        return distractors[:3]
    
    def _generate_concept_distractors(self, correct_cause: str) -> List[str]:
        """Generate distractors for concept questions"""
        generic_causes = [
            "Environmental factors",
            "Human intervention",
            "Natural processes",
            "External influences",
            "Internal mechanisms",
            "Random occurrence"
        ]
        
        # Filter out the correct cause if it's similar
        distractors = [cause for cause in generic_causes if cause.lower() != correct_cause.lower()]
        return distractors[:3]
    
    def analyze_text_difficulty(self, text: str) -> Dict[str, Any]:
        """Analyze text difficulty and suggest question types"""
        reading_ease = flesch_reading_ease(text)
        word_count = len(text.split())
        sentences = nltk.sent_tokenize(text)
        
        difficulty_level = "Easy" if reading_ease > 70 else "Medium" if reading_ease > 30 else "Hard"
        
        return {
            'reading_ease': reading_ease,
            'difficulty_level': difficulty_level,
            'word_count': word_count,
            'sentence_count': len(sentences),
            'recommended_questions': min(max(word_count // 100, 3), 10)
        }


# Integration with Flask app
def integrate_ai_generation():
    """Add AI question generation to existing Flask routes"""
    
    @app.route('/api/quiz/generate', methods=['POST'])
    def generate_ai_quiz():
        try:
            data = request.get_json()
            text = data.get('text', '')
            num_questions = data.get('num_questions', 5)
            
            if not text:
                return jsonify({'success': False, 'error': 'No text provided'})
            
            generator = AIQuestionGenerator()
            
            # Analyze text
            analysis = generator.analyze_text_difficulty(text)
            
            # Generate questions
            questions = generator.generate_questions(text, num_questions)
            
            return jsonify({
                'success': True,
                'questions': questions,
                'text_analysis': analysis,
                'message': f'Generated {len(questions)} questions successfully'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return app
