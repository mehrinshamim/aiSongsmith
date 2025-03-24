import torch
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from tqdm import tqdm
from .dataset import EmotionDataset

def train_model(model, texts, labels, epochs=3, batch_size=32, learning_rate=2e-5):
    """Train the emotion detection model"""
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )
    
    train_dataset = EmotionDataset(train_texts, train_labels, model.tokenizer)
    val_dataset = EmotionDataset(val_texts, val_labels, model.tokenizer)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    
    optimizer = torch.optim.AdamW(model.model.parameters(), lr=learning_rate)
    
    for epoch in range(epochs):
        model.model.train()
        total_loss = 0
        
        for batch in tqdm(train_loader, desc=f'Epoch {epoch + 1}/{epochs}'):
            input_ids = batch['input_ids'].to(model.device)
            attention_mask = batch['attention_mask'].to(model.device)
            labels = batch['labels'].to(model.device)
            
            outputs = model.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            loss = outputs.loss
            total_loss += loss.item()
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        
        # Validation
        model.model.eval()
        val_loss = 0
        predictions = []
        true_labels = []
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(model.device)
                attention_mask = batch['attention_mask'].to(model.device)
                labels = batch['labels'].to(model.device)
                
                outputs = model.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                val_loss += outputs.loss.item()
                predictions.extend(outputs.logits.argmax(dim=-1).cpu().numpy())
                true_labels.extend(labels.cpu().numpy())
        
        print(f'\nEpoch {epoch + 1}:')
        print(f'Average training loss: {total_loss / len(train_loader)}')
        print(f'Average validation loss: {val_loss / len(val_loader)}')
        print('\nClassification Report:')
        print(classification_report(true_labels, predictions, target_names=model.emotions))