server/
├── model/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── model_config.py        # Model hyperparameters and configurations
│   │   └── training_config.py     # Training settings
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── datasets/              # Raw dataset files
│   │   │   ├── goemotions/
│   │   │   ├── twitter_emotions/
│   │   │   └── custom_labels/
│   │   ├── preprocessed/          # Processed dataset files
│   │   ├── data_loader.py         # Dataset loading utilities
│   │   └── preprocessing.py       # Data preprocessing utilities
│   │
│   ├── emotion_detection/
│   │   ├── __init__.py
│   │   ├── dataset.py            # EmotionDataset class
│   │   ├── model.py              # EmotionDetector class
│   │   └── trainer.py            # Training logic
│   │
│   ├── music_processing/
│   │   ├── __init__.py
│   │   ├── audio_features.py     # Audio feature extraction
│   │   └── lyrics_analysis.py    # Lyrics processing
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── metrics.py            # Evaluation metrics
│   │   ├── logger.py             # Logging utilities
│   │   └── visualization.py      # Visualization tools
│   │
│   ├── checkpoints/              # Saved model checkpoints
│   │   └── .gitkeep
│   │
│   ├── logs/                     # Training logs
│   │   └── .gitkeep
│   │
│   └── tests/                    # Unit tests
│       ├── __init__.py
│       ├── test_emotion_detection.py
│       ├── test_data_loader.py
│       └── test_music_processing.py
│
├── requirements.txt              # Python dependencies
└── README.md                    # Documentation



to run emotion_detector
python -m server.model.emotion_detection