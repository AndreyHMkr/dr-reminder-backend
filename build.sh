#!/bin/bash

set -o errexit

pip install -r requirements.txt


echo "🔄 Applying migrations..."
python manage.py migrate

echo "✅ Build complete!"