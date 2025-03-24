from pathlib import Path
import pandas as pd
import logging

class DataLoader:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        
    def load_goemotions(self):
        """Load and preprocess GoEmotions dataset"""
        try:
            # Load data
            url = "https://raw.githubusercontent.com/google-research/google-research/master/goemotions/data/train.tsv"
            data = pd.read_csv(url, sep='\t')
            
            # Debug info
            self.logger.debug(f"Loaded columns: {data.columns.tolist()}")
            
            # Validate columns
            required_columns = ['text', 'emotion']
            if not all(col in data.columns for col in required_columns):
                available_cols = data.columns.tolist()
                raise ValueError(f"Required columns {required_columns} not found. Available columns: {available_cols}")
            
            emotion_map = {
                'joy': 'happy',
                'sadness': 'sad',
                'anger': 'angry',
                'fear': 'fear',
                'surprise': 'surprise',
                'love': 'love',
                'neutral': 'neutral'
            }
            
            # Extract text and labels with validation
            texts = data['text'].fillna('').tolist()
            raw_emotions = data['emotion'].fillna('neutral').tolist()
            
            # Map emotions with validation
            labels = []
            for emotion in raw_emotions:
                mapped_emotion = emotion_map.get(emotion, 'neutral')
                labels.append(mapped_emotion)
            
            # Validate output
            if not texts or not labels or len(texts) != len(labels):
                raise ValueError(f"Data validation failed: texts={len(texts)}, labels={len(labels)}")
                
            return texts, labels
            
        except pd.errors.EmptyDataError:
            self.logger.error("Empty dataset received")
            raise
        except KeyError as e:
            self.logger.error(f"Column not found: {e}")
            raise ValueError(f"Dataset structure error: {e}. Available columns: {data.columns.tolist()}")
        except Exception as e:
            self.logger.error(f"Error loading GoEmotions dataset: {e}")
            raise
    
    def load_twitter_emotions(self):
        """Load Twitter emotions dataset"""
        pass
    
    def load_custom_labels(self):
        """Load custom labeled data"""
        pass