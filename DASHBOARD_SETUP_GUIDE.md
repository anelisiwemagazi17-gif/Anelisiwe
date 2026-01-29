# Dashboard Setup & Integration Guide

## Quick Answer to Your Questions

### Q1: What do I need to do so the dashboard can fetch information from Moodle?
**Answer:** Nothing! It already works. The dashboard uses your Moodle API token from the `.env` file to fetch data directly from Moodle.

### Q2: If I generate and sign documents, will they appear on the dashboard?
**Answer:** Yes! Now they will. I just updated the system to automatically log all activities to the dashboard.

---

## How It Works Now

### Complete Integration Flow

```
1. Run: python -m src.main
   ↓
2. System creates dashboard record (status: pending)
   ↓
3. Validates data → Logs to dashboard
   ↓
4. Generates PDF → Updates dashboard (status: pdf_generated)
   ↓
5. Sends for signature → Updates dashboard (status: signature_sent)
   ↓
6. Gets signed PDF → Updates dashboard (status: signed)
   ↓
7. Uploads to Moodle → Updates dashboard (status: uploaded)
   ↓
8. View in dashboard: python run_dashboard.py
```

### What Gets Logged Automatically

Every time you run the main system, it now logs:

1. **SOR Request Creation**
   - Learner name, email, ID
   - Overall score
   - Timestamp

2. **Status Updates**
   - pending → pdf_generated → signature_sent → signed → uploaded
   - Or "failed" if any step fails

3. **Complete Audit Trail**
   - Process started
   - Validation passed/failed
   - PDF generated (with file path)
   - Signature sent (with request ID)
   - Signature completed
   - Upload success/failure

4. **Error Tracking**
   - Error messages if any step fails
   - Warnings for skipped steps

---

## Dashboard Features

### 1. Real-time Monitoring
- Open dashboard: `python run_dashboard.py`
- See all SOR requests and their statuses
- Search by learner name or email
- Filter by status (pending, signed, uploaded, failed)

### 2. Moodle Integration
The dashboard can check Moodle status for any learner:

**How to Check Moodle:**
1. Open dashboard
2. Double-click any learner row
3. Click "Check Moodle Status" button
4. See:
   - Submission status (submitted/not submitted)
   - Last modified timestamp
   - User ID verification

**What the Dashboard Checks:**
- Uses Moodle API token (no web login needed)
- Verifies if learner submitted assignment
- Shows submission timestamp
- Provides direct link to assignment

### 3. Detailed View
Double-click any row to see:
- Full request information
- PDF file paths (original and signed)
- Signature request ID
- Moodle submission status
- Complete activity log with timestamps

---

## Setup Steps (One-Time)

### Step 1: Ensure Dashboard Tables Exist
```bash
python setup_dashboard.py
```

This creates:
- `sor_requests` - Tracks all SOR generation requests
- `sor_audit_log` - Complete history of all actions
- `sor_settings` - Configuration settings

### Step 2: Verify Database Connection
```bash
python check_database.py
```

Should show:
- ✅ Database connection successful
- ✅ All required tables exist

### Step 3: Test Moodle Connection
```bash
python test_moodle.py
```

Should show:
- ✅ Connected to Moodle
- ✅ Assignment found
- ✅ Submissions retrieved

---

## Usage Workflow

### Generating SORs with Dashboard Tracking

**1. Run the automation:**
```bash
python -m src.main
```

**Output will show:**
```
📊 Dashboard tracking ID: 45
Started SOR generation for John Doe
✅ Validation passed
✅ PDF generated
⚠️  Skipping signature (SKIP_SIGNATURE=true)
✅ Uploaded to Moodle
```

**2. Open the dashboard:**
```bash
python run_dashboard.py
```

**3. You'll see:**
- New entry for "John Doe"
- Status: "uploaded"
- Overall score displayed
- All actions logged

**4. Check Moodle status:**
- Double-click the row
- Click "Check Moodle Status"
- See: "✅ Submission Found! Status: submitted"

---

## Dashboard Information Sources

### What Comes from Local Database
- Learner profile information
- Assessment results
- SOR request tracking
- PDF file paths
- Signature request IDs
- Audit log entries

### What Comes from Moodle API
- Assignment submission status
- Submission timestamps
- User ID verification
- Assignment details

### How Moodle Integration Works (Technical)

**No Web Login Required!**

The system uses:
1. **API Token** (from `.env` file)
   - Already configured: `MOODLE_TOKEN=xxxxx`
   - Has permission to read submissions

2. **Local User ID** (from database)
   - Avoids restricted Moodle user lookup API
   - Uses learner_id stored in local database

3. **Direct Submission Matching**
   - Fetches all assignment submissions
   - Matches by user ID
   - Returns submission status

**Example API Call:**
```python
# Dashboard checks Moodle like this:
submissions = moodle_service.get_submissions(assignment_id)
for submission in submissions:
    if submission['userid'] == learner_id:  # from local DB
        return {
            'found': True,
            'status': submission['status'],
            'timemodified': submission['timemodified']
        }
```

---

## Status Meanings

| Status | Description | What It Means |
|--------|-------------|---------------|
| **pending** | Just created | SOR request initiated |
| **pdf_generated** | PDF created | Document generated successfully |
| **signature_sent** | Sent for signing | Awaiting signature (if not skipped) |
| **signed** | Signature complete | Document signed |
| **uploaded** | Uploaded to Moodle | Process complete |
| **failed** | Error occurred | Check error_message for details |

---

## Troubleshooting

### Dashboard shows no data
1. **Check if you've run the main system:**
   ```bash
   python -m src.main
   ```
   This generates the data that appears in dashboard

2. **Click Refresh button** in dashboard

3. **Check database:**
   ```sql
   SELECT COUNT(*) FROM sor_requests;
   ```

### Moodle status check fails
1. **Verify Moodle token in `.env`:**
   ```
   MOODLE_TOKEN=your_actual_token
   ```

2. **Test Moodle connection:**
   ```bash
   python test_moodle.py
   ```

3. **Check assignment ID:**
   - Default from config: `ASSIGNMENT_COURSEMODULE_ID=22`
   - Update in `.env` if different

### Dashboard won't start
1. **Ensure database tables exist:**
   ```bash
   python setup_dashboard.py
   ```

2. **Check database connection:**
   ```bash
   python check_database.py
   ```

3. **Verify Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Example: Complete Workflow

### Scenario: Generate SOR for "SOR POD Internal POD"

**Step 1: Update `.env`**
```
TEST_LEARNER_NAME=SOR POD Internal POD
SKIP_SIGNATURE=true
```

**Step 2: Run automation**
```bash
python -m src.main
```

**Expected output:**
```
📊 Dashboard tracking ID: 1
✅ Process started
✅ Validation passed
✅ PDF generated: C:\...\output\MindWorx_Statement_of_Results_20260119_143022.pdf
⚠️  Signature skipped
✅ Uploaded to Moodle
```

**Step 3: Open dashboard**
```bash
python run_dashboard.py
```

**What you'll see:**
- Overview card showing 1 Total, 1 Uploaded
- Table row for "SOR POD Internal POD"
- Status: "uploaded" (green background)
- Overall score: displayed

**Step 4: Check Moodle**
- Double-click the row
- Click "Check Moodle Status"
- See: "✅ Submission Found! Status: submitted"

**Step 5: View in Moodle**
- Click "View in Moodle" button
- Opens browser to assignment page
- (You'll need to login to Moodle website)

---

## Advanced Features

### Search & Filter
- **Search box**: Type learner name or email
- **Status filter**: Dropdown to filter by status
- **Click column headers**: Sort by any column

### Audit Trail
- Every action is logged with timestamp
- View in details popup
- Shows success/error/warning status
- Includes detailed messages

### Overdue Tracking
- Automatically flags signatures pending > 7 days
- Shows in "Overdue" overview card
- Red flag indicator in table

### Color Coding
- 🟡 **Orange**: Pending
- 🔵 **Blue**: Awaiting signature
- 🟢 **Green**: Signed/Uploaded
- 🔴 **Red**: Failed

---

## Summary

### What You Asked
1. ✅ **Dashboard fetches Moodle info**: Already works via API token
2. ✅ **Documents appear in dashboard**: Now integrated automatically

### What Was Changed
- Updated `src/main.py` to log all actions to dashboard
- Updated `src/dashboard_db.py` to accept overall_score
- Every SOR generation now creates dashboard record
- Complete audit trail automatically logged

### What You Need to Do
**Nothing!** Just:
1. Run system: `python -m src.main`
2. Open dashboard: `python run_dashboard.py`
3. Everything is tracked automatically

### Next Steps
1. Run the automation for a test learner
2. Open dashboard to see it tracked
3. Check Moodle status from dashboard
4. View complete audit log

---

**You're all set! The system is fully integrated.**

When you generate documents, they automatically appear in the dashboard with complete tracking and Moodle integration.
