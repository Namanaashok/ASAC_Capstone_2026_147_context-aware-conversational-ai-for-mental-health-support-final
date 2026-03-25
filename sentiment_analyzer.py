class SentimentAnalyzer:
    def __init__(self):
        # A lightweight lexicon-based analyzer to avoid loading heavy HF models
        self.positive_words = {"good", "great", "excellent", "happy", "joy", "love", "wonderful", "better", "best", "calm", "peaceful", "okay", "fine", "amazing", "awesome", "fantastic", "relaxed", "content"}
        self.negative_words = {"bad", "sad", "angry", "depressed", "anxious", "terrible", "worst", "hate", "awful", "stress", "tired", "exhausted", "hard", "miserable", "hurt", "pain", "struggle", "overwhelmed"}

    def analyze(self, text):
        """Returns positive, negative, or neutral based on keyword matching."""
        if not text.strip():
            return "neutral"
            
        words = set(text.lower().replace('.', '').replace(',', '').replace('?', '').split())
        
        pos_count = len(words.intersection(self.positive_words))
        neg_count = len(words.intersection(self.negative_words))
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"

    def analyze_score(self, text):
        """Returns a numeric score (-1.0 to +1.0) for the mood tracker"""
        if not text.strip():
            return 0.0
            
        # Tokenize simply (remove punctuation)
        words = text.lower().replace('.', ' ').replace(',', ' ').replace('?', ' ').split()
        
        pos_count = sum(1 for w in words if w in self.positive_words)
        neg_count = sum(1 for w in words if w in self.negative_words)
        total_sentiment_words = pos_count + neg_count
        
        if total_sentiment_words == 0:
            return 0.0
            
        return (pos_count - neg_count) / total_sentiment_words
