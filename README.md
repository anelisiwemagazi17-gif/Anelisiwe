# MindWorx SOR Automation System

Automated Statement of Results (SOR) generation system for Pluto LMS / Moodle.

## Overview

This system automates the complete workflow for generating, signing, and uploading Statement of Results documents:

1. Fetches learner data from MySQL database
2. Validates learner information and quiz results
3. Generates professional PDF Statement of Results
4. Sends PDF for e-signature via Dropbox Sign
5. Waits for signature completion
6. Downloads signed document
7. Uploads to Moodle assignment

## Requirements

- Python 3.8 or higher
- MySQL database access
- Moodle LMS with API access
- Dropbox Sign API account

## Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your credentials:
   - Database connection details
   - Moodle URL and API token
   - Dropbox Sign API key
   - Optional: Custom image paths for logo, stamp, and cover

4. **Prepare image assets** (optional):
   - Logo image (PNG recommended)
   - Stamp image (PNG recommended)
   - Cover page image (PNG recommended)

   Update paths in `.env` or use defaults in `src/config.py`

## Usage

### Run the system:

```bash
python -m src.main
```

Or if running as a module:

```bash
cd "SOR Automation System"
python -m src.main
```

### Configuration

Edit [src/config.py](src/config.py) to customize:

- `TEST_LEARNER_NAME` - Learner to process
- `MAX_SIGNATURE_WAIT_MINUTES` - Maximum wait time for signature
- `ASSIGNMENT_COURSEMODULE_ID` - Moodle assignment ID
- Quiz weights and credits
- Qualification details

## Project Structure

```
SOR Automation System/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # Main entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database queries
│   ├── validation.py        # Data validation
│   ├── pdf_generator.py     # PDF generation with ReportLab
│   ├── signature_service.py # Dropbox Sign integration
│   └── moodle_upload.py     # Moodle file upload
├── .env                     # Environment variables (not in git)
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Features

### PDF Generation
- Professional multi-page PDF with cover page
- Watermarks and stamps
- Learner details and qualification structure
- Complete results breakdown with EISA scoring
- Provider declaration section

### E-Signature
- Automatic signature request via Dropbox Sign
- Configurable wait time and retry logic
- Status monitoring with progress updates

### Moodle Integration
- Direct file upload to assignment
- Fallback to manual database method
- Automatic submission tracking

## Troubleshooting

### Database Connection Issues
- Verify DB credentials in `.env`
- Check firewall/network access to database server
- Test connection using `db.test_connection()`

### Image Validation Errors
- Ensure image files exist at specified paths
- Use absolute paths for image locations
- Supported formats: PNG, JPG
- Check file permissions

### Signature Request Failures
- Verify Dropbox Sign API key is valid
- Check API rate limits
- Ensure learner email is valid
- Review test_mode setting (0 for production, 1 for test)

### Moodle Upload Issues
- Verify Moodle token has correct permissions
- Check assignment course module ID
- Ensure web services are enabled in Moodle
- Review Moodle logs for detailed errors

## Security Notes

- Never commit `.env` file to version control
- Keep API keys and database credentials secure
- Use environment variables for sensitive data
- Regularly rotate API tokens and passwords
- Use test mode for Dropbox Sign during development

## License

Copyright 2025 MindWorx Academy. All rights reserved.

## Support

For issues or questions, contact the development team.
