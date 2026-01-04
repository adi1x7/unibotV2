"""
NLP Intent Detection System for UniBot
Validates queries are college-domain only and detects intent
"""
from typing import Dict, Optional, Tuple
import re

class IntentDetector:
    """Detect intent and validate college-domain queries"""
    
    # College-related keywords
    COLLEGE_KEYWORDS = {
        'fees': ['fee', 'fees', 'tuition', 'cost', 'payment', 'scholarship', 'financial aid'],
        'admissions': ['admission', 'admissions', 'apply', 'application', 'eligibility', 'requirements', 'entrance', 'cutoff'],
        'exams': ['exam', 'examination', 'test', 'assessment', 'quiz', 'midterm', 'final', 'semester', 'registration'],
        'departments': ['department', 'department', 'course', 'program', 'curriculum', 'syllabus', 'subject'],
        'faculty': ['faculty', 'professor', 'teacher', 'staff', 'instructor', 'lecturer'],
        'hostels': ['hostel', 'hostels', 'accommodation', 'dormitory', 'residence', 'housing'],
        'general': ['college', 'university', 'campus', 'library', 'lab', 'laboratory', 'facility', 'facilities']
    }
    
    # Out-of-scope keywords (non-college related)
    OUT_OF_SCOPE_KEYWORDS = [
        'weather', 'news', 'sports', 'movie', 'music', 'recipe', 'cooking',
        'travel', 'hotel', 'restaurant', 'shopping', 'game', 'entertainment',
        'politics', 'stock', 'crypto', 'bitcoin', 'investment', 'trading','valentine','reels'
    ]
    
    def detect_intent(self, query: str) -> Tuple[Optional[str], float]:
        """
        Detect intent from query
        
        Args:
            query: User query string
            
        Returns:
            Tuple of (intent_category, confidence_score)
            Returns (None, 0.0) if out of scope
        """
        query_lower = query.lower()
        
        # Check if out of scope
        if self._is_out_of_scope(query_lower):
            return (None, 0.0)
        
        # Score each intent category
        intent_scores = {}
        for intent, keywords in self.COLLEGE_KEYWORDS.items():
            score = 0.0
            for keyword in keywords:
                if keyword in query_lower:
                    # Exact word match gets higher score
                    if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
                        score += 2.0
                    else:
                        score += 1.0
            
            if score > 0:
                intent_scores[intent] = score
        
        if not intent_scores:
            # No clear intent, but still college-related
            return ('general', 0.5)
        
        # Get intent with highest score
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        max_score = best_intent[1]
        
        # Normalize confidence (0.0 to 1.0)
        confidence = min(max_score / 10.0, 1.0)
        
        return (best_intent[0], confidence)
    
    def _is_out_of_scope(self, query_lower: str) -> bool:
        """Check if query is out of scope (not college-related)"""
        # Count college-related keywords
        college_count = 0
        for keywords in self.COLLEGE_KEYWORDS.values():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
                    college_count += 1
        
        # Count out-of-scope keywords
        out_of_scope_count = 0
        for keyword in self.OUT_OF_SCOPE_KEYWORDS:
            if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
                out_of_scope_count += 1
        
        # If out-of-scope keywords dominate, reject
        if out_of_scope_count > 0 and college_count == 0:
            return True
        
        # If query is very short and has no college keywords, might be out of scope
        if len(query_lower.split()) < 3 and college_count == 0:
            # Check for common greetings that are fine
            greetings = ['hello', 'hi', 'hey', 'help', 'thanks', 'thank you']
            if not any(greeting in query_lower for greeting in greetings):
                return True
        
        return False
    
    def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if query is college-domain only
        
        Args:
            query: User query string
            
        Returns:
            Tuple of (is_valid, rejection_message)
            If valid, returns (True, None)
            If invalid, returns (False, polite_rejection_message)
        """
        query_lower = query.lower()
        
        # Check if out of scope
        if self._is_out_of_scope(query_lower):
            return (False, 
                "I'm sorry, but I'm specifically designed to answer questions about the college, "
                "including fees, admissions, exams, departments, faculty, hostels, and other college-related topics. "
                "Could you please ask me something about the college instead?")
        
        # Query is valid
        return (True, None)
    
    def get_intent_info(self, query: str) -> Dict[str, any]:
        """
        Get detailed intent information
        
        Args:
            query: User query string
            
        Returns:
            Dictionary with intent, confidence, and validation info
        """
        intent, confidence = self.detect_intent(query)
        is_valid, rejection_msg = self.validate_query(query)
        
        return {
            'intent': intent,
            'confidence': confidence,
            'is_valid': is_valid,
            'rejection_message': rejection_msg
        }

