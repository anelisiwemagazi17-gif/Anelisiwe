# MindWorx SOR Dashboard

Professional desktop dashboard for managing and monitoring SOR (Statement of Results) automation.

![Dashboard Screenshot](dashboard_preview.png)

## Features

### 📊 Overview Dashboard
- **Real-time Statistics**: Total SORs, Pending, Signed, Uploaded, Failed, Overdue
- **Color-coded Cards**: Visual status indicators for quick assessment
- **Auto-refresh**: Keeps data up-to-date automatically

### 📋 Learner Management
- **Searchable Table**: Find learners quickly by name or email
- **Status Filtering**: Filter by status (Pending, Signed, Uploaded, etc.)
- **Sortable Columns**: Click column headers to sort
- **Color-coded Rows**: Visual indicators for different statuses
  - 🟡 Pending - Orange/Yellow background
  - 🔵 Awaiting Signature - Blue background
  - 🟢 Signed/Uploaded - Green background
  - 🔴 Failed - Red background

### 🚩 Smart Flags
- **Overdue Tracking**: Automatically flags signatures pending > 7 days
- **Failure Alerts**: Red flags for failed operations
- **Status Indicators**: Visual cues for each stage

### 📝 Audit Trail
- **Complete History**: Track every action for each SOR
- **Timestamps**: When each action occurred
- **Details View**: Double-click any row to see full details and audit log

### 📊 Document History
- **Per-Learner History**: View all SORs for a specific learner
- **Timeline View**: See when documents were generated, signed, uploaded
- **PDF Paths**: Quick access to generated documents

## Installation

### 1. Setup Database Tables

Run the setup script to create dashboard tables:

```bash
python setup_dashboard.py
```

This creates:
- `sor_requests` - Track all SOR generation requests
- `sor_audit_log` - Complete audit trail
- `sor_settings` - Dashboard configuration

### 2. Verify Installation

Check that tables were created:

```sql
SHOW TABLES LIKE 'sor_%';
```

You should see 3 tables.

## Usage

### Starting the Dashboard

```bash
python run_dashboard.py
```

Or on Windows, double-click: `run_dashboard.py`

### Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│  MindWorx SOR Dashboard              [↻ Refresh]            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  📊      ⏳       ✍️       ✅       ☁️      ❌       ⚠️      │
│  Total   Pending  Awaiting Signed  Uploaded Failed  Overdue │
│  127     15       8        45      42       3       2        │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  📋 All SOR Requests          🔍 Search: [_______] Status: [All]│
├─────────────────────────────────────────────────────────────┤
│  ID │ Learner Name    │ Email            │ Status    │ Score │
│  45 │ John Doe        │ john@example.com │ Signed    │ 85%   │
│  44 │ Jane Smith      │ jane@example.com │ Uploaded  │ 92%   │
│  43 │ Bob Johnson     │ bob@example.com  │ Pending   │ N/A   │
└─────────────────────────────────────────────────────────────┘
```

### Viewing Details

**Double-click any row** to see:
- Full request information
- PDF paths
- Signature request ID
- Complete audit log with timestamps

### Searching & Filtering

**Search**: Type in the search box to filter by learner name or email
**Filter by Status**: Use dropdown to show only specific statuses

### Refreshing Data

- Click **↻ Refresh** button in header
- Or close and reopen dashboard
- Auto-refresh coming soon!

## Integration with Automation System

The dashboard automatically tracks SOR requests when you run the automation.

### Automatic Logging (Coming Soon)

When you run `python -m src.main`, it will:
1. Create SOR request record
2. Update status as it progresses
3. Log all actions to audit trail
4. Track PDF paths and signature IDs

## Status Flow

```
pending
   ↓
pdf_generated
   ↓
signature_sent (if SKIP_SIGNATURE=false)
   ↓
signed
   ↓
uploaded
```

Failed status can occur at any stage.

## Database Schema

### sor_requests Table

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| learner_id | INT | Moodle user ID |
| learner_name | VARCHAR | Full name |
| learner_email | VARCHAR | Email address |
| status | ENUM | Current status |
| pdf_path | VARCHAR | Path to generated PDF |
| signed_pdf_path | VARCHAR | Path to signed PDF |
| signature_request_id | VARCHAR | Dropbox Sign request ID |
| overall_score | DECIMAL | Assessment score |
| created_at | TIMESTAMP | When created |
| updated_at | TIMESTAMP | Last update |
| error_message | TEXT | Error details if failed |

### sor_audit_log Table

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| sor_request_id | INT | Foreign key to sor_requests |
| action | VARCHAR | Action performed |
| details | TEXT | Additional information |
| status | ENUM | success/error/warning |
| user | VARCHAR | Who performed action |
| created_at | TIMESTAMP | When action occurred |

## Customization

### Change Overdue Threshold

Update in database:

```sql
UPDATE sor_settings
SET setting_value = '14'
WHERE setting_key = 'signature_timeout_days';
```

### Colors

Edit `dashboard.py`:

```python
self.colors = {
    'primary': '#2563eb',    # Blue
    'success': '#10b981',    # Green
    'warning': '#f59e0b',    # Orange
    'danger': '#ef4444',     # Red
    # ... customize as needed
}
```

## Troubleshooting

### Dashboard won't start

1. **Check database connection**:
   ```bash
   python check_database.py
   ```

2. **Verify tables exist**:
   ```sql
   SHOW TABLES LIKE 'sor_%';
   ```

3. **Re-run setup**:
   ```bash
   python setup_dashboard.py
   ```

### No data showing

1. **Check if tables have data**:
   ```sql
   SELECT COUNT(*) FROM sor_requests;
   ```

2. **Run automation** to generate test data
3. **Click Refresh** button

### Error messages

- Check `.env` file has correct database credentials
- Ensure MySQL server is running
- Check firewall isn't blocking connection

## Future Enhancements

Coming soon:
- ✅ Auto-refresh every 30 seconds
- ✅ Email reminders for overdue signatures
- ✅ Batch operations (bulk send, bulk upload)
- ✅ Export to Excel/CSV
- ✅ Charts and graphs
- ✅ LMS integration (when credentials available)
- ✅ Print/PDF export of dashboard
- ✅ Dark mode theme

## Support

For issues or feature requests, contact the development team.

---

**MindWorx SOR Automation Dashboard v1.0**
Built with Python & Tkinter
