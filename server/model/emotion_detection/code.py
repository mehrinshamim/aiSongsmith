# Import necessary libraries
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import requests
from tqdm import tqdm

class EmotionDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        # Tokenize the text
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class EmotionDetector:
    def __init__(self, num_labels=7, model_name='bert-base-uncased'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(
            model_name, 
            num_labels=num_labels
        ).to(self.device)
        
        # Define emotion labels
        self.emotions = ['happy', 'sad', 'angry', 'fear', 'surprise', 'love', 'neutral']
    
    def load_goemotions(self):
        """Load and preprocess GoEmotions dataset"""
        # Download GoEmotions dataset
        url = "https://raw.githubusercontent.com/google-research/google-research/master/goemotions/data/train.tsv"
        data = pd.read_csv(url, sep='\t')
        
        # Map emotions to our categories
        # This is a simplified mapping - you might want to adjust it
        emotion_map = {
            'joy': 'happy',
            'sadness': 'sad',
            'anger': 'angry',
            'fear': 'fear',
            'surprise': 'surprise',
            'love': 'love',
            'neutral': 'neutral'
        }       
        '''##################ADJUST THE MAPPING!!!--------------------------------'''
        
        # Process the data
        texts = data['text'].tolist()
        labels = data['emotion'].map(emotion_map).tolist()
        
        return texts, labels
    
    def train(self, texts, labels, epochs=3, batch_size=32, learning_rate=2e-5):
        """Train the emotion detection model"""
        # Split data
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=0.2, random_state=42
        )
        
        # Create datasets
        train_dataset = EmotionDataset(train_texts, train_labels, self.tokenizer)
        val_dataset = EmotionDataset(val_texts, val_labels, self.tokenizer)
        
        # Create dataloaders
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        # Initialize optimizer
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)
        
        # Training loop
        for epoch in range(epochs):
            self.model.train()
            total_loss = 0
            
            for batch in tqdm(train_loader, desc=f'Epoch {epoch + 1}/{epochs}'):
                # Move batch to device
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                total_loss += loss.item()
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            
            # Validation
            self.model.eval()
            val_loss = 0
            predictions = []
            true_labels = []
            
            with torch.no_grad():
                for batch in val_loader:
                    input_ids = batch['input_ids'].to(self.device)
                    attention_mask = batch['attention_mask'].to(self.device)
                    labels = batch['labels'].to(self.device)
                    
                    outputs = self.model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        labels=labels
                    )
                    
                    val_loss += outputs.loss.item()
                    predictions.extend(outputs.logits.argmax(dim=-1).cpu().numpy())
                    true_labels.extend(labels.cpu().numpy())
            
            # Print metrics
            print(f'\nEpoch {epoch + 1}:')
            print(f'Average training loss: {total_loss / len(train_loader)}')
            print(f'Average validation loss: {val_loss / len(val_loader)}')
            print('\nClassification Report:')
            print(classification_report(true_labels, predictions, target_names=self.emotions))
    
    def predict(self, text):
        """Predict emotions for a given text"""
        self.model.eval()
        
        # Tokenize input text
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        # Move to device
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            probabilities = torch.softmax(outputs.logits, dim=-1)
        
        # Convert to emotion predictions with confidence scores
        predictions = []
        for probs in probabilities:
            emotion_scores = {
                emotion: float(prob)
                for emotion, prob in zip(self.emotions, probs)
            }
            predictions.append(emotion_scores)
        
        return predictions[0]

# Example usage
def main():
    # Initialize detector
    detector = EmotionDetector()
    
    # Load and prepare data
    texts, labels = detector.load_goemotions()
    
    # Train the model
    detector.train(texts, labels)
    
    # Make predictions
    text = "I'm feeling really excited about my upcoming vacation!"
    predictions = detector.predict(text)
    
    # Print predictions
    print("\nEmotion Predictions:")
    for emotion, score in predictions.items():
        print(f"{emotion}: {score:.4f}")

if __name__ == "__main__":
    main()