"""
Short Note Generator Module
Automatically generates concise study notes from uploaded documents in simple English
"""
import re
import nltk
from typing import List, Dict, Any
from collections import Counter
import textwrap

class ShortNoteGenerator:
    """Generates concise study notes from text content"""
    
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger')
    
    def generate_notes(self, text: str, note_style: str = "bullet") -> Dict[str, Any]:
        """
        Generate short notes from text
        
        Args:
            text: Input text content
            note_style: Style of notes - 'bullet', 'numbered', 'paragraph', 'flashcard'
        
        Returns:
            Dictionary containing generated notes and metadata
        """
        # Clean and preprocess text
        cleaned_text = self._clean_text(text)
        
        # Extract key information
        key_points = self._extract_key_points(cleaned_text)
        definitions = self._extract_definitions(cleaned_text)
        important_facts = self._extract_important_facts(cleaned_text)
        summary = self._create_summary(cleaned_text)
        
        # Generate notes based on style
        if note_style == "bullet":
            formatted_notes = self._format_bullet_notes(key_points, definitions, important_facts)
        elif note_style == "numbered":
            formatted_notes = self._format_numbered_notes(key_points, definitions, important_facts)
        elif note_style == "paragraph":
            formatted_notes = self._format_paragraph_notes(summary, key_points)
        elif note_style == "flashcard":
            formatted_notes = self._format_flashcard_notes(definitions, important_facts)
        else:
            formatted_notes = self._format_bullet_notes(key_points, definitions, important_facts)
        
        return {
            'success': True,
            'notes': formatted_notes,
            'summary': summary,
            'key_points_count': len(key_points),
            'definitions_count': len(definitions),
            'facts_count': len(important_facts),
            'original_word_count': len(text.split()),
            'notes_word_count': len(formatted_notes.split()),
            'compression_ratio': round(len(formatted_notes.split()) / len(text.split()) * 100, 1)
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess the input text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # Fix common issues
        text = text.replace('\n', ' ').replace('\t', ' ')
        
        return text.strip()
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from the text"""
        sentences = nltk.sent_tokenize(text)
        key_points = []
        
        # Look for sentences with key indicators
        key_indicators = [
            'important', 'key', 'main', 'primary', 'essential', 'crucial',
            'significant', 'major', 'fundamental', 'basic', 'critical',
            'remember', 'note that', 'it is important', 'must understand'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 150:  # Reasonable length
                # Check for key indicators
                if any(indicator in sentence.lower() for indicator in key_indicators):
                    simplified = self._simplify_sentence(sentence)
                    key_points.append(simplified)
                
                # Look for sentences with numbers/statistics
                elif re.search(r'\d+', sentence):
                    simplified = self._simplify_sentence(sentence)
                    key_points.append(simplified)
                
                # Look for sentences starting with action words
                elif sentence.lower().startswith(('this', 'these', 'the process', 'the method')):
                    simplified = self._simplify_sentence(sentence)
                    key_points.append(simplified)
        
        # Remove duplicates and limit to top 8 points
        unique_points = list(dict.fromkeys(key_points))
        return unique_points[:8]
    
    def _extract_definitions(self, text: str) -> List[Dict[str, str]]:
        """Extract definitions from the text"""
        sentences = nltk.sent_tokenize(text)
        definitions = []
        
        # Patterns for definitions
        definition_patterns = [
            r'(.+?) is (.+?)\.?$',
            r'(.+?) are (.+?)\.?$',
            r'(.+?) means (.+?)\.?$',
            r'(.+?) refers to (.+?)\.?$',
            r'(.+?) can be defined as (.+?)\.?$',
            r'(.+?) is known as (.+?)\.?$'
        ]
        
        for sentence in sentences:
            if len(sentence) > 20 and len(sentence) < 200:
                for pattern in definition_patterns:
                    match = re.search(pattern, sentence, re.IGNORECASE)
                    if match:
                        term = match.group(1).strip()
                        definition = match.group(2).strip()
                        
                        # Clean up term and definition
                        term = re.sub(r'^(the|a|an)\s+', '', term.lower()).title()
                        definition = self._simplify_sentence(definition)
                        
                        if len(term) < 50 and len(definition) < 150:
                            definitions.append({
                                'term': term,
                                'definition': definition
                            })
                        break
        
        # Remove duplicates and limit
        unique_definitions = []
        seen_terms = set()
        for def_item in definitions:
            if def_item['term'].lower() not in seen_terms:
                unique_definitions.append(def_item)
                seen_terms.add(def_item['term'].lower())
        
        return unique_definitions[:6]
    
    def _extract_important_facts(self, text: str) -> List[str]:
        """Extract important facts and statistics"""
        sentences = nltk.sent_tokenize(text)
        facts = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 15 and len(sentence) < 120:
                # Look for sentences with numbers
                if re.search(r'\d+', sentence):
                    facts.append(self._simplify_sentence(sentence))
                
                # Look for cause and effect
                elif any(word in sentence.lower() for word in ['because', 'due to', 'results in', 'causes', 'leads to']):
                    facts.append(self._simplify_sentence(sentence))
                
                # Look for comparison
                elif any(word in sentence.lower() for word in ['compared to', 'unlike', 'whereas', 'while', 'however']):
                    facts.append(self._simplify_sentence(sentence))
        
        return facts[:5]
    
    def _simplify_sentence(self, sentence: str) -> str:
        """Simplify sentence to use simpler English"""
        # Common word replacements for simpler English
        replacements = {
            'utilize': 'use',
            'demonstrate': 'show',
            'implement': 'put in place',
            'facilitate': 'help',
            'commence': 'start',
            'terminate': 'end',
            'subsequently': 'then',
            'furthermore': 'also',
            'nevertheless': 'however',
            'accordingly': 'so',
            'therefore': 'so',
            'consequently': 'as a result',
            'approximately': 'about',
            'sufficient': 'enough',
            'numerous': 'many',
            'acquire': 'get',
            'assist': 'help',
            'attempt': 'try',
            'construct': 'build',
            'examine': 'look at',
            'indicate': 'show',
            'maintain': 'keep',
            'obtain': 'get',
            'previous': 'earlier',
            'require': 'need',
            'significant': 'important'
        }
        
        # Apply replacements
        words = sentence.split()
        simplified_words = []
        
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word in replacements:
                # Preserve capitalization and punctuation
                if word[0].isupper():
                    replacement = replacements[clean_word].capitalize()
                else:
                    replacement = replacements[clean_word]
                
                # Add back punctuation
                punct = ''.join([c for c in word if not c.isalnum()])
                simplified_words.append(replacement + punct)
            else:
                simplified_words.append(word)
        
        return ' '.join(simplified_words)
    
    def _create_summary(self, text: str) -> str:
        """Create a brief summary of the text"""
        sentences = nltk.sent_tokenize(text)
        
        # Score sentences based on importance indicators
        sentence_scores = {}
        
        for i, sentence in enumerate(sentences):
            score = 0
            words = sentence.lower().split()
            
            # First and last sentences get bonus points
            if i == 0 or i == len(sentences) - 1:
                score += 2
            
            # Sentences with numbers
            if re.search(r'\d+', sentence):
                score += 1
            
            # Sentences with key words
            key_words = ['important', 'main', 'key', 'significant', 'major', 'primary']
            score += sum(1 for word in key_words if word in words)
            
            # Length bonus (not too short, not too long)
            if 50 <= len(sentence) <= 150:
                score += 1
            
            sentence_scores[sentence] = score
        
        # Get top 3 sentences
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Sort by original order
        selected_sentences = []
        for sentence in sentences:
            if any(sentence == item[0] for item in top_sentences):
                selected_sentences.append(self._simplify_sentence(sentence))
        
        return ' '.join(selected_sentences)
    
    def _format_bullet_notes(self, key_points: List[str], definitions: List[Dict], facts: List[str]) -> str:
        """Format notes as bullet points"""
        notes = "📝 **STUDY NOTES**\n\n"
        
        if key_points:
            notes += "🔑 **Key Points:**\n"
            for point in key_points:
                notes += f"• {point}\n"
            notes += "\n"
        
        if definitions:
            notes += "📚 **Important Terms:**\n"
            for def_item in definitions:
                notes += f"• **{def_item['term']}**: {def_item['definition']}\n"
            notes += "\n"
        
        if facts:
            notes += "💡 **Important Facts:**\n"
            for fact in facts:
                notes += f"• {fact}\n"
        
        return notes
    
    def _format_numbered_notes(self, key_points: List[str], definitions: List[Dict], facts: List[str]) -> str:
        """Format notes as numbered list"""
        notes = "📝 **STUDY NOTES**\n\n"
        counter = 1
        
        if key_points:
            notes += "🔑 **Key Points:**\n"
            for point in key_points:
                notes += f"{counter}. {point}\n"
                counter += 1
            notes += "\n"
        
        if definitions:
            notes += "📚 **Important Terms:**\n"
            for def_item in definitions:
                notes += f"{counter}. **{def_item['term']}**: {def_item['definition']}\n"
                counter += 1
            notes += "\n"
        
        if facts:
            notes += "💡 **Important Facts:**\n"
            for fact in facts:
                notes += f"{counter}. {fact}\n"
                counter += 1
        
        return notes
    
    def _format_paragraph_notes(self, summary: str, key_points: List[str]) -> str:
        """Format notes as paragraphs"""
        notes = "📝 **STUDY NOTES**\n\n"
        
        notes += "📖 **Summary:**\n"
        notes += f"{summary}\n\n"
        
        if key_points:
            notes += "🔑 **Main Ideas:**\n"
            notes += "The key concepts to remember are: " + ", ".join(key_points[:5]) + ".\n\n"
        
        return notes
    
    def _format_flashcard_notes(self, definitions: List[Dict], facts: List[str]) -> str:
        """Format notes as flashcards"""
        notes = "🃏 **FLASHCARD NOTES**\n\n"
        
        if definitions:
            notes += "📚 **Term Cards:**\n"
            for i, def_item in enumerate(definitions, 1):
                notes += f"**Card {i}:**\n"
                notes += f"Front: What is {def_item['term']}?\n"
                notes += f"Back: {def_item['definition']}\n\n"
        
        if facts:
            notes += "💡 **Fact Cards:**\n"
            for i, fact in enumerate(facts, len(definitions) + 1):
                notes += f"**Card {i}:**\n"
                notes += f"Fact: {fact}\n\n"
        
        return notes

# Integration with Flask app
def add_note_generator_routes(app):
    """Add note generator routes to Flask app"""
    
    @app.route('/api/notes/generate', methods=['POST'])
    def generate_notes():
        try:
            data = request.get_json()
            text = data.get('text', '')
            note_style = data.get('style', 'bullet')  # bullet, numbered, paragraph, flashcard
            
            if not text:
                return jsonify({'success': False, 'error': 'No text provided'})
            
            generator = ShortNoteGenerator()
            result = generator.generate_notes(text, note_style)
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/notes/styles', methods=['GET'])
    def get_note_styles():
        """Get available note styles"""
        styles = [
            {
                'id': 'bullet',
                'name': 'Bullet Points',
                'description': 'Organized bullet points with key topics',
                'icon': 'fas fa-list-ul'
            },
            {
                'id': 'numbered',
                'name': 'Numbered List',
                'description': 'Sequential numbered points for easy reference',
                'icon': 'fas fa-list-ol'
            },
            {
                'id': 'paragraph',
                'name': 'Summary Paragraphs',
                'description': 'Flowing summary with main ideas',
                'icon': 'fas fa-align-left'
            },
            {
                'id': 'flashcard',
                'name': 'Flashcards',
                'description': 'Question and answer format for studying',
                'icon': 'fas fa-layer-group'
            }
        ]
        
        return jsonify({
            'success': True,
            'styles': styles
        })
    
    return app
