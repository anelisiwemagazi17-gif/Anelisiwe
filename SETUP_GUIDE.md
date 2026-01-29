# SOR Automation System - Complete Setup Guide for New Laptop

## Prerequisites
- Windows 10 or 11
- Internet connection
- Administrator access

---

## Step 1: Install Python

1. **Download Python:**
   - Go to https://www.python.org/downloads/
   - Download Python 3.8 or higher (recommended: Python 3.11)

2. **Install Python:**
   - Run the installer
   - ✅ **IMPORTANT:** Check "Add Python to PATH"
   - Click "Install Now"

3. **Verify Installation:**
   ```bash
   python --version
   pip --version
   ```

---

## Step 2: Transfer Project Files

1. Copy the entire "SOR Automation System" folder to your new laptop
2. Recommended location: `C:\Users\[YourUsername]\Desktop\SOR Automation System`

---

## Step 3: Install Required Libraries

Open Command Prompt (cmd) or PowerShell and run:

```bash
# Navigate to project directory
cd "C:\Users\[YourUsername]\Desktop\SOR Automation System"

# Install all required packages
pip install -r requirements.txt
```

**Alternative (install manually):**
```bash
pip install python-dotenv==1.0.0
pip install pymysql==1.1.0
pip install requests==2.31.0
pip install reportlab==4.0.7
pip install Pillow
pip install pandas==2.1.4
pip install numpy==1.26.2
pip install cryptography==41.0.7
```

---

## Step 4: Copy Image Files

Copy these image files to your Desktop:
- `Mindworx_logo.png`
- `Mindworx_ Stamp.png`
- `Mindworx Cover page.png`
- `Mindworx_dashboard.png`

Place them in: `C:\Users\[YourUsername]\Desktop\`

---

## Step 5: Configure .env File

The `.env` file should already be in the project folder with these settings:

```env
# Database Configuration
DB_HOST=sql39.cpt3.host-h.net
DB_USER=mindwuejax_1
DB_PASSWORD=zS07NwN90b4LlMNyRpIu
DB_NAME=mindworx_academy_db
DB_PORT=3306

# Moodle Configuration
MOODLE_URL=https://lms.mindworx.co.za/academy
MOODLE_TOKEN=f990caa93ac25a203152266e38d18e27

# Dropbox Sign API
DROPBOX_SIGN_API_KEY=0c08fa10aeb5add0dd07772bc193a8b06c5154816ad3a69a3251317a669884fa

# Workflow Options
SKIP_SIGNATURE=false

# Image paths (update with your username)
LOGO_PATH=C:\Users\[YourUsername]\Desktop\Mindworx_logo.png
STAMP_PATH=C:\Users\[YourUsername]\Desktop\Mindworx_ Stamp.png
COVER_PATH=C:\Users\[YourUsername]\Desktop\Mindworx Cover page.png
```

**Update the image paths** with your actual username!

---

## Step 6: Update config.py

Edit `src\config.py` and update the `TEST_LEARNER_NAME`:

```python
TEST_LEARNER_NAME = "Your Test Learner Name"
```

---

## Step 7: Test the Installation

### Test Database Connection:
```bash
cd "C:\Users\[YourUsername]\Desktop\SOR Automation System"
python -c "from src.database import db; db.test_connection()"
```

### Test Moodle Connection:
```bash
python test_moodle_token.py
```

---

## Step 8: Run the Dashboard

```bash
cd "C:\Users\[YourUsername]\Desktop\SOR Automation System"
python run_dashboard.py
```

The dashboard should open in a new window!

---

## Step 9: Generate a Test SOR (Optional)

```bash
cd "C:\Users\[YourUsername]\Desktop\SOR Automation System"
python -m src.main
```

This will:
1. Fetch learner data
2. Generate PDF
3. Send for signature (if SKIP_SIGNATURE=false)
4. Upload to Moodle

---

## Common Issues & Solutions

### Issue: "python is not recognized"
**Solution:** Python not in PATH. Reinstall Python and check "Add Python to PATH"

### Issue: "No module named 'dotenv'"
**Solution:** Run `pip install python-dotenv`

### Issue: "Cannot connect to database"
**Solution:** Check internet connection and `.env` file credentials

### Issue: "Image not found"
**Solution:** Update image paths in `.env` with correct username

### Issue: "tkinter not found"
**Solution:** Reinstall Python and ensure tkinter is selected during installation

---

## Project Structure

```
SOR Automation System/
├── src/
│   ├── config.py          # Configuration settings
│   ├── database.py        # Database connection
│   ├── dashboard.py       # Main dashboard GUI
│   ├── dashboard_db.py    # Dashboard database operations
│   ├── moodle_service.py  # Moodle API integration
│   ├── pdf_generator.py   # PDF generation
│   ├── signature_service.py # Dropbox Sign integration
│   ├── moodle_upload.py   # Moodle upload functionality
│   └── validation.py      # Data validation
├── .env                   # Environment variables (credentials)
├── requirements.txt       # Python dependencies
├── run_dashboard.py       # Dashboard launcher
├── test_moodle_token.py   # Moodle token tester
├── update_scores.py       # Score updater utility
└── SETUP_GUIDE.md        # This file
```

---

## Quick Reference Commands

```bash
# Navigate to project
cd "C:\Users\[YourUsername]\Desktop\SOR Automation System"

# Run Dashboard
python run_dashboard.py

# Generate SOR
python -m src.main

# Test Moodle Token
python test_moodle_token.py

# Update Scores
python update_scores.py

# Install Dependencies
pip install -r requirements.txt
```

---

## Support

For issues or questions, check the project documentation or contact the system administrator.
