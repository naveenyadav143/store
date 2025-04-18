# settings.py

import os  # Ensure os is imported if not already

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Define BASE_DIR if missing

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']  # Restrict to local development

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Ensure this points to the correct templates directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Add your context processors here
            ],
        },
    },
]