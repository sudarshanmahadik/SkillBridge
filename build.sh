#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Initialize and seed database tables automatically on build/deploy
python init_db.py
