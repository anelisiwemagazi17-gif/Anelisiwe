# MindWorx SOR Automation - Moodle Plugin Installation Guide

## Overview

The `local_sor` plugin provides web service APIs for:
- SOR submission management
- Automated grading
- Bulk grade operations
- Grade release workflows

## Requirements

- Moodle 4.0 or higher
- PHP 7.4 or higher
- Admin access to Moodle server

## Installation Steps

### Step 1: Copy Plugin Files

Copy the `local_sor` folder to your Moodle installation:

```bash
# On the Moodle server
cp -r local_sor /path/to/moodle/local/
```

The folder structure should be:
```
moodle/
└── local/
    └── sor/
        ├── version.php
        ├── db/
        │   └── services.php
        ├── classes/
        │   └── external/
        │       ├── submission_api.php
        │       └── grading_api.php
        └── lang/
            └── en/
                └── local_sor.php
```

### Step 2: Install Plugin in Moodle

1. Login to Moodle as administrator
2. Go to **Site administration** → **Notifications**
3. Moodle will detect the new plugin and prompt for installation
4. Click **Upgrade Moodle database now**
5. Confirm the installation

### Step 3: Enable Web Services

1. Go to **Site administration** → **Plugins** → **Web services** → **Overview**
2. Ensure the following are enabled:
   - Enable web services: ✓
   - Enable protocols: REST protocol ✓

### Step 4: Create External Service

1. Go to **Site administration** → **Plugins** → **Web services** → **External services**
2. Find "MindWorx SOR Automation" service (created automatically)
3. Or create a custom service with these functions:
   - `local_sor_get_submission_status`
   - `local_sor_submit_sor_file`
   - `local_sor_get_all_submissions`
   - `local_sor_grade_submission`
   - `local_sor_bulk_grade_submissions`
   - `local_sor_get_grading_status`
   - `local_sor_release_grades`

### Step 5: Generate API Token

1. Go to **Site administration** → **Plugins** → **Web services** → **Manage tokens**
2. Click **Create token**
3. Select a user with appropriate permissions (admin or teacher)
4. Select "MindWorx SOR Automation" service
5. Copy the generated token

### Step 6: Configure SOR Automation System

Update your `config.py` with the new token:

```python
MOODLE_TOKEN = "your_generated_token_here"
```

## Available Web Service Functions

### Submission Functions

| Function | Description |
|----------|-------------|
| `local_sor_get_submission_status` | Get submission status for a user |
| `local_sor_submit_sor_file` | Submit SOR PDF file |
| `local_sor_get_all_submissions` | Get all submissions for assignment |

### Grading Functions

| Function | Description |
|----------|-------------|
| `local_sor_grade_submission` | Grade a single submission |
| `local_sor_bulk_grade_submissions` | Grade multiple submissions |
| `local_sor_get_grading_status` | Get grading progress |
| `local_sor_release_grades` | Release grades to students |

## API Examples

### Grade a Submission

```python
# Using the Python dashboard
from src.moodle_service import moodle_service

result = moodle_service.grade_submission(
    assignment_id=5,
    user_id=123,
    grade=85.5,
    feedback="Good work on the assessment!"
)
```

### Bulk Grade Submissions

```python
grades = [
    {'userid': 123, 'grade': 85.5, 'feedback': 'Good work!'},
    {'userid': 124, 'grade': 92.0, 'feedback': 'Excellent!'},
    {'userid': 125, 'grade': 78.0, 'feedback': 'Needs improvement'},
]

result = moodle_service.bulk_grade_submissions(assignment_id=5, grades=grades)
```

### Get Grading Status

```python
status = moodle_service.get_grading_status(assignment_id=5)
print(f"Graded: {status['graded']}/{status['totalsubmissions']}")
```

## Troubleshooting

### Token Permission Error

If you get permission errors, ensure the token user has:
- `mod/assign:view`
- `mod/assign:submit`
- `mod/assign:grade`

### Plugin Not Detected

1. Check file permissions on the plugin folder
2. Verify the folder structure matches the required layout
3. Check Moodle error logs at **Site administration** → **Reports** → **Logs**

### Web Service Errors

Enable debugging in Moodle:
1. **Site administration** → **Development** → **Debugging**
2. Set debug messages to "DEVELOPER"
3. Check error details in API responses

## Support

For issues with the SOR Automation System, contact MindWorx support.
