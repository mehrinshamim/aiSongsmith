from pathlib import Path
import pandas as pd

class DataLoader:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
    
    def load_goemotions(self):
        """Load GoEmotions dataset"""
        pass
    
    def load_twitter_emotions(self):
        """Load Twitter emotions dataset"""
        pass
    
    def load_custom_labels(self):
        """Load custom labeled data"""
        pass