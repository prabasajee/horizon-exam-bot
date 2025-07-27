"""
Enhanced AI-Powered Note Generation for Horizon Exam Bot
Advanced NLP features, multiple note formats, and intelligent content analysis
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
from collections import Counter
import requests
from textstat import flesch_reading_ease, flesch_kincaid_grade
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag

class EnhancedNoteGenerator:
    """Advanced note generator with AI-powered features"""
    
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.ensure_nltk_data()
    
    def ensure_nltk_data(self):
        """Ensure required NLTK data is downloaded"""
        required_data = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
        for data in required_data:
            try:
                nltk.data.find(f'tokenizers/{data}')
            except LookupError:
                nltk.download(data, quiet=True)
    
    def generate_comprehensive_notes(self, text: str, style: str = "comprehensive", options: Dict = None) -> Dict[str, Any]:
        """Generate comprehensive study notes with advanced analysis"""
        if not options:
            options = {}
        
        try:
            # Analyze text complexity and readability
            analysis = self.analyze_text_complexity(text)
            
            # Extract various types of content
            content_analysis = self.extract_comprehensive_content(text)
            
            # Generate notes based on style
            formatted_notes = self.format_advanced_notes(content_analysis, style, options)
            
            # Generate study aids
            study_aids = self.generate_study_aids(content_analysis, text)
            
            # Create summary statistics
            stats = self.generate_content_statistics(text, content_analysis)
            
            return {
                'success': True,
                'notes': formatted_notes,
                'content_analysis': content_analysis,
                'text_analysis': analysis,
                'study_aids': study_aids,
                'statistics': stats,
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'style': style,
                    'options': options,
                    'version': '2.0'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'style': style
                }
            }
    
    def analyze_text_complexity(self, text: str) -> Dict[str, Any]:
        """Analyze text complexity and readability"""
        sentences = sent_tokenize(text)
        words = word_tokenize(text.lower())
        
        # Filter out non-alphabetic tokens
        words = [word for word in words if word.isalpha()]
        
        # Calculate various metrics
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        unique_words = len(set(words))
        vocabulary_density = unique_words / len(words) if words else 0
        
        # Readability scores
        try:
            flesch_score = flesch_reading_ease(text)
            grade_level = flesch_kincaid_grade(text)
        except:
            flesch_score = 50  # Default moderate score
            grade_level = 10   # Default grade level
        
        # Determine complexity level
        if flesch_score >= 70:
            complexity = "Easy"
        elif flesch_score >= 50:
            complexity = "Moderate"
        elif flesch_score >= 30:
            complexity = "Difficult"
        else:
            complexity = "Very Difficult"
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'unique_words': unique_words,
            'vocabulary_density': round(vocabulary_density, 3),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'flesch_reading_ease': round(flesch_score, 2),
            'grade_level': round(grade_level, 2),
            'complexity_level': complexity,
            'estimated_reading_time': round(len(words) / 200, 1)  # Assuming 200 WPM
        }
    
    def extract_comprehensive_content(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive content analysis"""
        sentences = sent_tokenize(text)
        
        return {
            'key_concepts': self.extract_key_concepts(text),
            'definitions': self.extract_advanced_definitions(text),
            'important_facts': self.extract_important_facts(text),
            'processes': self.extract_processes(text),
            'examples': self.extract_examples(text),
            'numbers_and_statistics': self.extract_numbers_and_stats(text),
            'named_entities': self.extract_named_entities(text),
            'relationships': self.extract_relationships(text),
            'questions': self.generate_potential_questions(text),
            'summary': self.create_intelligent_summary(text),
            'topic_hierarchy': self.create_topic_hierarchy(text)
        }
    
    def extract_key_concepts(self, text: str) -> List[Dict[str, Any]]:
        """Extract key concepts using advanced NLP techniques"""
        sentences = sent_tokenize(text)
        concepts = []
        
        # Look for definition patterns and important statements
        concept_patterns = [
            r'(.+?) is (?:an?|the) (.+?)(?:\.|,|;)',
            r'(.+?) (?:refers to|means|represents) (.+?)(?:\.|,|;)',
            r'(?:The|A) (?:concept of|idea of|principle of) (.+?) (?:is|involves|includes) (.+?)(?:\.|,|;)',
            r'(?:Important|Key|Main|Primary|Essential) (.+?) (?:is|are|include) (.+?)(?:\.|,|;)'
        ]
        
        for sentence in sentences:
            # Skip very short sentences
            if len(sentence.split()) < 8:
                continue
            
            for pattern in concept_patterns:
                matches = re.finditer(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    concept = match.group(1).strip()
                    description = match.group(2).strip()
                    
                    if len(concept) < 100 and len(description) < 200:
                        concepts.append({
                            'concept': self.clean_concept_text(concept),
                            'description': self.clean_concept_text(description),
                            'source_sentence': sentence,
                            'importance_score': self.calculate_importance_score(sentence)
                        })
        
        # Remove duplicates and sort by importance
        unique_concepts = []
        seen_concepts = set()
        
        for concept in sorted(concepts, key=lambda x: x['importance_score'], reverse=True):
            concept_key = concept['concept'].lower()
            if concept_key not in seen_concepts and len(concept_key) > 3:
                seen_concepts.add(concept_key)
                unique_concepts.append(concept)
        
        return unique_concepts[:10]  # Return top 10 concepts
    
    def extract_advanced_definitions(self, text: str) -> List[Dict[str, Any]]:
        """Extract definitions with context and examples"""
        sentences = sent_tokenize(text)
        definitions = []
        
        definition_patterns = [
            r'(.+?) is defined as (.+?)(?:\.|,|;)',
            r'(.+?) can be defined as (.+?)(?:\.|,|;)',
            r'(.+?) is (?:a|an) (.+?) that (.+?)(?:\.|,|;)',
            r'(?:A|An) (.+?) is (.+?)(?:\.|,|;)',
            r'(.+?) (?:means|refers to|denotes) (.+?)(?:\.|,|;)'
        ]
        
        for sentence in sentences:
            for pattern in definition_patterns:
                matches = re.finditer(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    term = match.group(1).strip()
                    definition = match.group(2).strip()
                    
                    # Combine parts if there's a third group
                    if len(match.groups()) > 2:
                        definition += f" that {match.group(3).strip()}"
                    
                    if 3 <= len(term) <= 50 and 10 <= len(definition) <= 300:
                        definitions.append({
                            'term': self.clean_concept_text(term),
                            'definition': self.clean_concept_text(definition),
                            'context': sentence,
                            'type': self.classify_definition_type(definition)
                        })
        
        return definitions[:8]
    
    def extract_processes(self, text: str) -> List[Dict[str, Any]]:
        """Extract step-by-step processes and procedures"""
        sentences = sent_tokenize(text)
        processes = []
        
        # Look for process indicators
        process_indicators = [
            'steps', 'process', 'procedure', 'method', 'algorithm', 'workflow',
            'first', 'second', 'third', 'then', 'next', 'finally', 'lastly'
        ]
        
        current_process = None
        process_steps = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check if sentence indicates a new process
            if any(indicator in sentence_lower for indicator in ['process', 'steps', 'procedure', 'method']):
                if current_process and process_steps:
                    processes.append({
                        'name': current_process,
                        'steps': process_steps,
                        'step_count': len(process_steps)
                    })
                
                current_process = sentence
                process_steps = []
            
            # Check if sentence is a step
            elif any(indicator in sentence_lower for indicator in ['first', 'second', 'then', 'next', 'step']):
                if len(sentence.split()) >= 5:  # Meaningful step
                    step_number = len(process_steps) + 1
                    process_steps.append({
                        'step_number': step_number,
                        'description': sentence,
                        'keywords': self.extract_step_keywords(sentence)
                    })
        
        # Add the last process if any
        if current_process and process_steps:
            processes.append({
                'name': current_process,
                'steps': process_steps,
                'step_count': len(process_steps)
            })
        
        return processes
    
    def extract_examples(self, text: str) -> List[Dict[str, Any]]:
        """Extract examples and case studies"""
        sentences = sent_tokenize(text)
        examples = []
        
        example_patterns = [
            r'(?:for example|for instance|such as|including|like) (.+?)(?:\.|,|;)',
            r'(?:an example (?:of|is)|examples include) (.+?)(?:\.|,|;)',
            r'(?:consider|imagine|suppose) (.+?)(?:\.|,|;)'
        ]
        
        for sentence in sentences:
            for pattern in example_patterns:
                matches = re.finditer(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    example_text = match.group(1).strip()
                    
                    if 10 <= len(example_text) <= 200:
                        examples.append({
                            'example': example_text,
                            'context': sentence,
                            'type': 'illustration'
                        })
        
        return examples[:6]
    
    def extract_numbers_and_stats(self, text: str) -> List[Dict[str, Any]]:
        """Extract numerical data and statistics"""
        sentences = sent_tokenize(text)
        stats = []
        
        # Pattern to find numbers with context
        number_pattern = r'(\d+(?:\.\d+)?(?:%|percent|dollars?|years?|months?|days?|hours?|minutes?|seconds?)?)'
        
        for sentence in sentences:
            numbers = re.finditer(number_pattern, sentence, re.IGNORECASE)
            for match in numbers:
                number = match.group(1)
                context = sentence
                
                # Extract more context around the number
                start_pos = max(0, match.start() - 50)
                end_pos = min(len(sentence), match.end() + 50)
                detailed_context = sentence[start_pos:end_pos]
                
                stats.append({
                    'value': number,
                    'context': detailed_context,
                    'full_sentence': sentence,
                    'type': self.classify_number_type(number, context)
                })
        
        return stats[:10]
    
    def extract_named_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities (people, places, organizations)"""
        # Tokenize and tag parts of speech
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)
        
        # Perform named entity recognition
        entities = ne_chunk(tagged)
        
        entity_dict = {
            'PERSON': [],
            'ORGANIZATION': [],
            'GPE': [],  # Geopolitical entities (countries, cities, states)
            'OTHER': []
        }
        
        for chunk in entities:
            if hasattr(chunk, 'label'):
                entity_name = ' '.join([token for token, pos in chunk.leaves()])
                entity_type = chunk.label()
                
                if entity_type in entity_dict:
                    if entity_name not in entity_dict[entity_type]:
                        entity_dict[entity_type].append(entity_name)
                else:
                    if entity_name not in entity_dict['OTHER']:
                        entity_dict['OTHER'].append(entity_name)
        
        return entity_dict
    
    def generate_potential_questions(self, text: str) -> List[Dict[str, str]]:
        """Generate potential study questions from content"""
        sentences = sent_tokenize(text)
        questions = []
        
        # Question templates based on content patterns
        question_templates = [
            ("What is", "definition"),
            ("How does", "process"),
            ("Why is", "explanation"),
            ("When did", "temporal"),
            ("Where does", "location"),
            ("Who was", "person"),
            ("List the", "enumeration"),
            ("Compare", "comparison"),
            ("Explain the difference between", "contrast")
        ]
        
        content_analysis = self.extract_comprehensive_content(text)
        
        # Generate questions from key concepts
        for concept in content_analysis.get('key_concepts', [])[:5]:
            questions.append({
                'question': f"What is {concept['concept']}?",
                'type': 'definition',
                'difficulty': 'easy',
                'hint': concept['description'][:50] + '...'
            })
        
        # Generate questions from processes
        for process in content_analysis.get('processes', [])[:3]:
            questions.append({
                'question': f"Describe the process mentioned in: {process['name'][:50]}...",
                'type': 'process',
                'difficulty': 'medium',
                'hint': f"This process has {process['step_count']} main steps"
            })
        
        return questions[:10]
    
    def create_intelligent_summary(self, text: str) -> Dict[str, str]:
        """Create an intelligent summary using multiple techniques"""
        sentences = sent_tokenize(text)
        
        # Score sentences based on various factors
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            score = self.calculate_sentence_importance(sentence, text)
            sentence_scores.append((sentence, score, i))
        
        # Sort by score and select top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Create different summary lengths
        summaries = {
            'brief': self.create_summary_by_length(sentence_scores, max_sentences=3),
            'standard': self.create_summary_by_length(sentence_scores, max_sentences=5),
            'detailed': self.create_summary_by_length(sentence_scores, max_sentences=8)
        }
        
        return summaries
    
    def format_advanced_notes(self, content_analysis: Dict, style: str, options: Dict) -> str:
        """Format notes using advanced styling options"""
        if style == "comprehensive":
            return self.format_comprehensive_notes(content_analysis, options)
        elif style == "outline":
            return self.format_outline_notes(content_analysis, options)
        elif style == "mind_map":
            return self.format_mind_map_notes(content_analysis, options)
        elif style == "cornell":
            return self.format_cornell_notes(content_analysis, options)
        elif style == "flashcard_advanced":
            return self.format_advanced_flashcards(content_analysis, options)
        else:
            return self.format_comprehensive_notes(content_analysis, options)
    
    def format_comprehensive_notes(self, content: Dict, options: Dict) -> str:
        """Format comprehensive notes with all extracted content"""
        notes = "📚 **COMPREHENSIVE STUDY NOTES**\\n\\n"
        
        # Add summary
        if content.get('summary'):
            notes += "📖 **Executive Summary:**\\n"
            notes += content['summary'].get('standard', '') + "\\n\\n"
        
        # Add key concepts
        if content.get('key_concepts'):
            notes += "🎯 **Key Concepts:**\\n"
            for concept in content['key_concepts'][:6]:
                notes += f"• **{concept['concept']}**: {concept['description']}\\n"
            notes += "\\n"
        
        # Add definitions
        if content.get('definitions'):
            notes += "📚 **Important Definitions:**\\n"
            for definition in content['definitions'][:5]:
                notes += f"• **{definition['term']}**: {definition['definition']}\\n"
            notes += "\\n"
        
        # Add processes
        if content.get('processes'):
            notes += "⚙️ **Processes & Procedures:**\\n"
            for process in content['processes'][:2]:
                notes += f"**{process['name']}**\\n"
                for step in process['steps']:
                    notes += f"  {step['step_number']}. {step['description']}\\n"
                notes += "\\n"
        
        # Add examples
        if content.get('examples'):
            notes += "💡 **Examples:**\\n"
            for example in content['examples'][:4]:
                notes += f"• {example['example']}\\n"
            notes += "\\n"
        
        # Add statistics
        if content.get('numbers_and_statistics'):
            notes += "📊 **Key Statistics:**\\n"
            for stat in content['numbers_and_statistics'][:5]:
                notes += f"• {stat['context']}\\n"
            notes += "\\n"
        
        return notes
    
    def format_cornell_notes(self, content: Dict, options: Dict) -> str:
        """Format notes in Cornell note-taking style"""
        notes = "📝 **CORNELL NOTES**\\n\\n"
        notes += "=" * 50 + "\\n"
        notes += "**CUES** | **NOTES**\\n"
        notes += "=" * 50 + "\\n"
        
        # Main notes section
        if content.get('key_concepts'):
            for concept in content['key_concepts'][:5]:
                cue = concept['concept'][:15] + "..."
                note = concept['description']
                notes += f"{cue:<15} | {note}\\n"
        
        notes += "\\n" + "=" * 50 + "\\n"
        notes += "**SUMMARY:**\\n"
        if content.get('summary'):
            notes += content['summary'].get('brief', '') + "\\n"
        
        return notes
    
    def generate_study_aids(self, content_analysis: Dict, original_text: str) -> Dict[str, Any]:
        """Generate various study aids"""
        return {
            'flashcards': self.create_smart_flashcards(content_analysis),
            'practice_questions': content_analysis.get('questions', []),
            'key_terms_glossary': self.create_glossary(content_analysis),
            'study_schedule': self.suggest_study_schedule(original_text),
            'memory_techniques': self.suggest_memory_techniques(content_analysis)
        }
    
    def create_smart_flashcards(self, content: Dict) -> List[Dict[str, str]]:
        """Create intelligent flashcards from content"""
        flashcards = []
        
        # Flashcards from definitions
        for definition in content.get('definitions', [])[:8]:
            flashcards.append({
                'front': f"What is {definition['term']}?",
                'back': definition['definition'],
                'type': 'definition',
                'difficulty': 'medium'
            })
        
        # Flashcards from key concepts
        for concept in content.get('key_concepts', [])[:5]:
            flashcards.append({
                'front': f"Explain the concept: {concept['concept']}",
                'back': concept['description'],
                'type': 'concept',
                'difficulty': 'medium'
            })
        
        return flashcards
    
    def suggest_study_schedule(self, text: str) -> Dict[str, Any]:
        """Suggest a study schedule based on content complexity"""
        analysis = self.analyze_text_complexity(text)
        
        # Base study time on complexity and length
        base_study_time = analysis['estimated_reading_time'] * 3  # 3x reading time for study
        
        if analysis['complexity_level'] == 'Very Difficult':
            study_sessions = max(4, int(base_study_time / 30))
        elif analysis['complexity_level'] == 'Difficult':
            study_sessions = max(3, int(base_study_time / 45))
        else:
            study_sessions = max(2, int(base_study_time / 60))
        
        return {
            'total_study_time': round(base_study_time, 1),
            'recommended_sessions': study_sessions,
            'session_length': round(base_study_time / study_sessions, 1),
            'schedule': self.create_study_timeline(study_sessions)
        }
    
    # Helper methods
    def clean_concept_text(self, text: str) -> str:
        """Clean and format concept text"""
        # Remove extra whitespace and clean up
        text = re.sub(r'\\s+', ' ', text.strip())
        # Remove leading articles
        text = re.sub(r'^(the|a|an)\\s+', '', text, flags=re.IGNORECASE)
        return text
    
    def calculate_importance_score(self, sentence: str) -> float:
        """Calculate importance score for a sentence"""
        score = 0.0
        
        # Length factor (moderate length preferred)
        word_count = len(sentence.split())
        if 10 <= word_count <= 25:
            score += 0.2
        
        # Keyword indicators
        important_keywords = ['important', 'key', 'main', 'primary', 'essential', 'crucial', 'significant']
        for keyword in important_keywords:
            if keyword in sentence.lower():
                score += 0.3
        
        # Position factor (first few sentences often important)
        # This would need to be implemented with context of position in text
        
        return score
    
    def calculate_sentence_importance(self, sentence: str, full_text: str) -> float:
        """Calculate sentence importance for summarization"""
        words = word_tokenize(sentence.lower())
        words = [w for w in words if w.isalpha() and w not in self.stop_words]
        
        # Word frequency in document
        full_words = word_tokenize(full_text.lower())
        word_freq = Counter(full_words)
        
        # Calculate score
        score = sum(word_freq[word] for word in words) / len(words) if words else 0
        return score
    
    def classify_definition_type(self, definition: str) -> str:
        """Classify the type of definition"""
        if any(word in definition.lower() for word in ['process', 'method', 'procedure']):
            return 'process'
        elif any(word in definition.lower() for word in ['theory', 'concept', 'principle']):
            return 'concept'
        elif any(word in definition.lower() for word in ['tool', 'device', 'instrument']):
            return 'object'
        else:
            return 'general'
    
    def extract_step_keywords(self, step_text: str) -> List[str]:
        """Extract keywords from a process step"""
        words = word_tokenize(step_text.lower())
        # Filter for important words (nouns, verbs, adjectives)
        tagged = pos_tag(words)
        keywords = [word for word, pos in tagged if pos.startswith(('NN', 'VB', 'JJ')) and len(word) > 3]
        return keywords[:5]
    
    def classify_number_type(self, number: str, context: str) -> str:
        """Classify the type of numerical data"""
        context_lower = context.lower()
        
        if '%' in number or 'percent' in context_lower:
            return 'percentage'
        elif any(word in context_lower for word in ['year', 'date', 'century']):
            return 'temporal'
        elif any(word in context_lower for word in ['dollar', 'cost', 'price']):
            return 'monetary'
        elif any(word in context_lower for word in ['meter', 'foot', 'inch', 'mile']):
            return 'measurement'
        else:
            return 'quantity'
    
    def create_summary_by_length(self, scored_sentences: List[Tuple], max_sentences: int) -> str:
        """Create summary with specified sentence count"""
        # Select top sentences and sort by original order
        selected = scored_sentences[:max_sentences]
        selected.sort(key=lambda x: x[2])  # Sort by original position
        
        summary = ' '.join([sentence for sentence, score, pos in selected])
        return summary
    
    def create_glossary(self, content: Dict) -> List[Dict[str, str]]:
        """Create a glossary of terms"""
        glossary = []
        
        # Add definitions
        for definition in content.get('definitions', []):
            glossary.append({
                'term': definition['term'],
                'definition': definition['definition'],
                'type': 'definition'
            })
        
        # Add key concepts
        for concept in content.get('key_concepts', []):
            glossary.append({
                'term': concept['concept'],
                'definition': concept['description'],
                'type': 'concept'
            })
        
        # Sort alphabetically
        glossary.sort(key=lambda x: x['term'].lower())
        
        return glossary
    
    def suggest_memory_techniques(self, content: Dict) -> List[Dict[str, str]]:
        """Suggest memory techniques based on content"""
        techniques = []
        
        if content.get('processes'):
            techniques.append({
                'technique': 'Acronyms',
                'description': 'Create acronyms for process steps',
                'application': 'Use first letters of each step to create memorable words'
            })
        
        if content.get('numbers_and_statistics'):
            techniques.append({
                'technique': 'Number Association',
                'description': 'Associate numbers with familiar concepts',
                'application': 'Link statistical values to dates or quantities you know'
            })
        
        if len(content.get('key_concepts', [])) > 5:
            techniques.append({
                'technique': 'Mind Palace',
                'description': 'Visualize concepts in familiar locations',
                'application': 'Place each concept in a room of your house'
            })
        
        return techniques
    
    def create_study_timeline(self, sessions: int) -> List[Dict[str, str]]:
        """Create a study timeline"""
        timeline = []
        
        session_types = ['Review', 'Deep Study', 'Practice', 'Review']
        
        for i in range(sessions):
            session_type = session_types[i % len(session_types)]
            timeline.append({
                'session': f"Session {i + 1}",
                'type': session_type,
                'focus': self.get_session_focus(session_type),
                'day': f"Day {i + 1}"
            })
        
        return timeline
    
    def get_session_focus(self, session_type: str) -> str:
        """Get focus area for different session types"""
        focus_map = {
            'Review': 'Quick review of key concepts and definitions',
            'Deep Study': 'Detailed analysis of complex topics and processes',
            'Practice': 'Test yourself with questions and flashcards',
            'Synthesis': 'Connect concepts and create comprehensive understanding'
        }
        return focus_map.get(session_type, 'General study session')
    
    def create_topic_hierarchy(self, text: str) -> Dict[str, Any]:
        """Create a hierarchical structure of topics"""
        # This is a simplified version - in production, you'd use more sophisticated NLP
        sentences = sent_tokenize(text)
        
        # Simple topic extraction based on sentence patterns
        topics = {
            'main_topics': [],
            'subtopics': [],
            'supporting_details': []
        }
        
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in ['chapter', 'section', 'part']):
                topics['main_topics'].append(sentence)
            elif len(sentence.split()) >= 15:  # Longer sentences often contain subtopics
                topics['subtopics'].append(sentence)
            else:
                topics['supporting_details'].append(sentence)
        
        return topics
    
    def generate_content_statistics(self, original_text: str, content_analysis: Dict) -> Dict[str, Any]:
        """Generate comprehensive content statistics"""
        return {
            'content_breakdown': {
                'key_concepts': len(content_analysis.get('key_concepts', [])),
                'definitions': len(content_analysis.get('definitions', [])),
                'processes': len(content_analysis.get('processes', [])),
                'examples': len(content_analysis.get('examples', [])),
                'statistics': len(content_analysis.get('numbers_and_statistics', []))
            },
            'study_aids_generated': {
                'flashcards': len(content_analysis.get('questions', [])),
                'practice_questions': len(content_analysis.get('questions', [])),
                'glossary_terms': len(content_analysis.get('definitions', [])) + len(content_analysis.get('key_concepts', []))
            },
            'extraction_efficiency': {
                'concepts_per_paragraph': round(len(content_analysis.get('key_concepts', [])) / max(1, original_text.count('\\n\\n')), 2),
                'definitions_per_1000_words': round(len(content_analysis.get('definitions', [])) / max(1, len(original_text.split()) / 1000), 2)
            }
        }
