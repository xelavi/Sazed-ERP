$ErrorActionPreference = 'Stop'

Write-Host 'Installing backend Python dependencies...' -ForegroundColor Cyan

python -m pip install --upgrade pip setuptools wheel

# Core dependencies (development + production)
python -m pip install `
  "Django>=5.1,<6.0" `
  "djangorestframework>=3.15" `
  "django-cors-headers>=4.3" `
  "django-filter>=24.0" `
  "python-decouple>=3.8" `
  "dj-database-url>=2.1" `
  "psycopg[binary]>=3.2" `
  "whitenoise>=6.5" `
  "Pillow>=10.0" `
  "gunicorn>=22.0" `
  "reportlab>=4.0" `
  "qrcode[pil]>=7.4"

Write-Host 'Done. Installed backend dependencies successfully.' -ForegroundColor Green
