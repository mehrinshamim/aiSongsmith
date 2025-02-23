# Configuration for models
MODEL_CONFIG = {
    'emotion_detection': {
        'model_name': 'bert-base-uncased',
        'num_labels': 7,
        'max_length': 128,
        'dropout': 0.1
    },
    'music_processing': {
        'sample_rate': 22050,
        'hop_length': 512,
        'n_mels': 128
    }
}