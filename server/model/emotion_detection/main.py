from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
import datetime
from .model import EmotionDetector
from .trainer import train_model
from ..data.data_loader import DataLoader

def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Create a fixed log filename (without timestamp)
    log_file = log_dir / 'emotion_detection.log'
    
    # Configure rotating file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,  # Keep 5 backup files
        encoding='utf-8'
    )
    
    # Configure logging format
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(log_format)
    
    # Configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Log separator and initial message
    logger = logging.getLogger(__name__)
    logger.info("-" * 80)  # Add a separator line
    logger.info("New logging session started")
    logger.info(f"Logging initialized. Log file: {log_file}")

def main():
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Setup paths
        current_dir = Path(__file__).parent
        data_dir = current_dir.parent / 'data'
        
        # Initialize data loader and detector
        logger.info("Initializing data loader and detector")
        data_loader = DataLoader(data_dir)
        detector = EmotionDetector()
        
        # Load and prepare data
        logger.info("Loading GoEmotions dataset")
        texts, labels = data_loader.load_goemotions()
        logger.info(f"Loaded {len(texts)} samples")
        
        # Train the model
        logger.info("Starting model training")
        train_model(detector, texts, labels)
        
        # Make predictions
        text = "I'm feeling really excited about my upcoming vacation!"
        logger.info(f"Making prediction for text: {text}")
        predictions = detector.predict(text)
        
        # Print predictions
        print("\nEmotion Predictions:")
        for emotion, score in predictions.items():
            print(f"{emotion}: {score:.4f}")
            
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    main()