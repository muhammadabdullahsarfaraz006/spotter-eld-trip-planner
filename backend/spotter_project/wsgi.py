"""
WSGI config for spotter_project.
"""
import os
import sys
from pathlib import Path

# Add backend directory to sys.path so spotter_project and apps are importable
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spotter_project.settings")

application = get_wsgi_application()
