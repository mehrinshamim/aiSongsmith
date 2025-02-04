aiSongsmith/
├── backend/  #django
│   ├── manage.py
│   ├── aiSongsmith/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── songsmith/
│       ├── models.py
│       ├── serializers.py
│       ├── urls.py
│       └── views/
│           ├── spotify_auth.py
│           ├── player.py
│           └── recommendations.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Player.jsx
│   │   │   ├── Recommendations.jsx
│   │   │   └── SpotifyAuth.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   └── App.jsx
│   └── package.json
└── requirements.txt