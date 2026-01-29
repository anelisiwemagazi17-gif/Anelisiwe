import os
from dotenv import load_dotenv
from .config import config, get_pdf_output_path
from .database import db
from .validation import validator
from .pdf_generator import generate_sor_pdf, validate_image_path, calculate_overall_score
from .signature_service import send_signature_request, wait_for_signature, download_signed_document
from .moodle_upload import upload_to_assignment_direct
from .dashboard_db import dashboard_db

load_dotenv()

# Global image validation (run once)
print("=" * 60)
print("IMAGE VALIDATION")
print("=" * 60)
config.LOGO_PATH_VALID = validate_image_path(config.LOGO_PATH, "LOGO")
config.STAMP_PATH_VALID = validate_image_path(config.STAMP_PATH, "STAMP")
config.COVER_PATH_VALID = validate_image_path(config.COVER_PATH, "COVER")

print("\n" + "=" * 60)
print("VALIDATION SUMMARY")
print("=" * 60)
for name, path in [("LOGO", config.LOGO_PATH_VALID), ("STAMP", config.STAMP_PATH_VALID), ("COVER", config.COVER_PATH_VALID)]:
    status = "READY" if path else "NOT AVAILABLE"
    print(f"  {name}: {status}")
print("=" * 60 + "\n")

def main():
    # Validate config and DB
    if not config.validate_config():
        return
    if not db.test_connection():
        return

    learner_name = config.TEST_LEARNER_NAME
    learner_data = db.fetch_all_learner_data(learner_name)
    if not learner_data:
        print("[X] No learner data found. Exiting.")
        return

    # Get learner info for dashboard
    learner_id = learner_data['learner']['id']
    learner_email = learner_data['learner'].get('email', 'N/A')
    overall_score = calculate_overall_score(learner_data)

    # Create SOR request in dashboard
    sor_id = dashboard_db.create_sor_request(learner_id, learner_name, learner_email, overall_score)
    print(f"\n[DASHBOARD] Tracking ID: {sor_id}")
    dashboard_db.log_action(sor_id, 'process_started', f'Started SOR generation for {learner_name}', 'success')

    # Validate learner data
    report = validator.validate_all(learner_data)
    report.print_report()
    if report.has_errors():
        print("[X] Validation errors present. Fix and retry.")
        dashboard_db.update_sor_request(sor_id, {
            'status': 'failed',
            'error_message': 'Validation errors present'
        })
        dashboard_db.log_action(sor_id, 'validation_failed', 'Validation errors found', 'error')
        return

    dashboard_db.log_action(sor_id, 'validation_passed', 'All validation checks passed', 'success')

    # Generate PDF
    output_pdf = str(get_pdf_output_path())
    pdf_path = generate_sor_pdf(learner_name, learner_data, output_pdf)
    if not pdf_path:
        print("[X] PDF generation failed.")
        dashboard_db.update_sor_request(sor_id, {
            'status': 'failed',
            'error_message': 'PDF generation failed'
        })
        dashboard_db.log_action(sor_id, 'pdf_generation_failed', 'PDF generation failed', 'error')
        return

    # Update dashboard with PDF path
    dashboard_db.update_sor_request(sor_id, {
        'status': 'pdf_generated',
        'pdf_path': pdf_path
    })
    dashboard_db.log_action(sor_id, 'pdf_generated', f'PDF generated: {pdf_path}', 'success')

    # Determine which PDF to upload
    if config.SKIP_SIGNATURE:
        print("\n[!]  Skipping signature step (SKIP_SIGNATURE=true)")
        print("   Using unsigned PDF for upload")
        upload_pdf_path = pdf_path
        dashboard_db.log_action(sor_id, 'signature_skipped', 'Signature step skipped (SKIP_SIGNATURE=true)', 'warning')
    else:
        # Send for signature
        sig_id = send_signature_request(pdf_path, learner_email, learner_name)
        if not sig_id:
            print("[X] Failed to create signature request.")
            dashboard_db.update_sor_request(sor_id, {
                'status': 'failed',
                'error_message': 'Failed to create signature request'
            })
            dashboard_db.log_action(sor_id, 'signature_request_failed', 'Failed to send signature request', 'error')
            return

        # Update dashboard with signature ID
        dashboard_db.update_sor_request(sor_id, {
            'status': 'signature_sent',
            'signature_request_id': sig_id
        })
        dashboard_db.log_action(sor_id, 'signature_sent', f'Signature request sent (ID: {sig_id})', 'success')

        # Wait and download signed PDF
        signed = wait_for_signature(sig_id, max_wait_minutes=config.MAX_SIGNATURE_WAIT_MINUTES, check_interval=config.SIGNATURE_CHECK_INTERVAL_SECONDS)
        if not signed:
            print("[TIMEOUT]  Signature not completed in time.")
            dashboard_db.log_action(sor_id, 'signature_timeout', f'Signature not completed within {config.MAX_SIGNATURE_WAIT_MINUTES} minutes', 'warning')
            return

        dashboard_db.log_action(sor_id, 'signature_completed', 'Document signed successfully', 'success')

        signed_pdf_path = pdf_path.replace(".pdf", "_SIGNED.pdf")
        if not download_signed_document(sig_id, signed_pdf_path, max_retries=config.MAX_DOWNLOAD_RETRIES, retry_delay=config.DOWNLOAD_RETRY_DELAY_SECONDS):
            print("[X] Failed to download signed PDF.")
            dashboard_db.update_sor_request(sor_id, {
                'status': 'failed',
                'error_message': 'Failed to download signed PDF'
            })
            dashboard_db.log_action(sor_id, 'download_failed', 'Failed to download signed PDF', 'error')
            return

        # Update dashboard with signed PDF path
        dashboard_db.update_sor_request(sor_id, {
            'status': 'signed',
            'signed_pdf_path': signed_pdf_path
        })
        dashboard_db.log_action(sor_id, 'signed_pdf_downloaded', f'Signed PDF downloaded: {signed_pdf_path}', 'success')
        upload_pdf_path = signed_pdf_path

    # Upload to Moodle
    upload_result = upload_to_assignment_direct(upload_pdf_path, learner_name, learner_data['learner']['id'], config.ASSIGNMENT_COURSEMODULE_ID)
    if upload_result:
        print("[OK] Upload completed:", upload_result)
        dashboard_db.update_sor_request(sor_id, {
            'status': 'uploaded'
        })
        dashboard_db.log_action(sor_id, 'moodle_upload_success', f'Uploaded to Moodle - File: {upload_result.get("filename", "N/A")}', 'success')
    else:
        print("[X] Upload failed.")
        dashboard_db.update_sor_request(sor_id, {
            'status': 'failed',
            'error_message': 'Moodle upload failed'
        })
        dashboard_db.log_action(sor_id, 'moodle_upload_failed', 'Failed to upload to Moodle', 'error')

    if upload_result:
        print(f"\nUpload successful!")
        print(f"   Filename: {upload_result['filename']}")
        print(f"   Method: {upload_result['method']}")
        print(f"   Submission ID: {upload_result.get('submission_id', 'N/A')}")

        print(f"\nCheck in Moodle:")
        print(f"   1. Go to: {config.MOODLE_URL}/mod/assign/view.php?id=213")
        print(f"   2. Click 'View all submissions'")
        print(f"   3. Look for: {learner_name}")
        print(f"   4. File should be in 'File submissions' column")
    else:
        print(f"\nUpload failed")

    print("\n" + "=" * 60)
    print("Process completed successfully!")
    print("=" * 60)

    print(f"\nGenerated Files:")
    print(f"   Original SOR: {pdf_path}")
    if not config.SKIP_SIGNATURE:
        print(f"   Signed SOR: {upload_pdf_path}")
    else:
        print(f"   (Signature step was skipped)")

def process_pending_requests():
    """Process all pending SOR requests - called by API"""
    results = {
        'processed': 0,
        'success': 0,
        'failed': 0,
        'errors': []
    }

    try:
        # Get all pending requests
        pending_requests = dashboard_db.get_all_sor_requests(limit=100)
        pending = [r for r in pending_requests if r['status'] == 'pending']

        if not pending:
            return {'processed': 0, 'message': 'No pending requests'}

        for req in pending:
            results['processed'] += 1
            try:
                sor_id = req['id']
                learner_name = req['learner_name']

                # Fetch learner data from database
                learner_data = db.fetch_all_learner_data(learner_name)
                if not learner_data:
                    dashboard_db.update_sor_request(sor_id, {
                        'status': 'failed',
                        'error_message': 'Learner data not found'
                    })
                    dashboard_db.log_action(sor_id, 'process_failed', 'Learner data not found in database', 'error')
                    results['failed'] += 1
                    results['errors'].append(f"ID {sor_id}: Learner data not found")
                    continue

                # Calculate overall score
                overall_score = calculate_overall_score(learner_data)

                # Validate learner data
                report = validator.validate_all(learner_data)
                if report.has_errors():
                    dashboard_db.update_sor_request(sor_id, {
                        'status': 'failed',
                        'error_message': 'Validation errors'
                    })
                    dashboard_db.log_action(sor_id, 'validation_failed', 'Validation errors found', 'error')
                    results['failed'] += 1
                    results['errors'].append(f"ID {sor_id}: Validation failed")
                    continue

                dashboard_db.log_action(sor_id, 'validation_passed', 'Validation passed', 'success')

                # Generate PDF
                output_pdf = str(get_pdf_output_path())
                pdf_path = generate_sor_pdf(learner_name, learner_data, output_pdf)

                if not pdf_path:
                    dashboard_db.update_sor_request(sor_id, {
                        'status': 'failed',
                        'error_message': 'PDF generation failed'
                    })
                    dashboard_db.log_action(sor_id, 'pdf_generation_failed', 'PDF generation failed', 'error')
                    results['failed'] += 1
                    results['errors'].append(f"ID {sor_id}: PDF generation failed")
                    continue

                # Update status to pdf_generated
                dashboard_db.update_sor_request(sor_id, {
                    'status': 'pdf_generated',
                    'pdf_path': pdf_path,
                    'overall_score': overall_score
                })
                dashboard_db.log_action(sor_id, 'pdf_generated', f'PDF generated: {pdf_path}', 'success')

                # Send for signature if not skipping
                if not config.SKIP_SIGNATURE:
                    learner_email = req.get('learner_email') or learner_data['learner'].get('email')
                    if learner_email:
                        sig_id = send_signature_request(pdf_path, learner_email, learner_name)
                        if sig_id:
                            dashboard_db.update_sor_request(sor_id, {
                                'status': 'signature_sent',
                                'signature_request_id': sig_id
                            })
                            dashboard_db.log_action(sor_id, 'signature_sent', f'Signature request sent (ID: {sig_id})', 'success')
                        else:
                            dashboard_db.log_action(sor_id, 'signature_failed', 'Failed to send signature request', 'warning')

                results['success'] += 1

            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"ID {req.get('id', '?')}: {str(e)}")
                print(f"[ERROR] Processing request {req.get('id')}: {e}")

        return results

    except Exception as e:
        return {'error': str(e), 'processed': results['processed']}


def check_signature_status():
    """Check status of all pending signatures - called by API"""
    results = {
        'checked': 0,
        'completed': 0,
        'pending': 0,
        'uploaded': 0,
        'errors': []
    }

    try:
        # Get all requests with signature_sent status
        all_requests = dashboard_db.get_all_sor_requests(limit=100)
        signature_pending = [r for r in all_requests if r['status'] == 'signature_sent' and r.get('signature_request_id')]

        if not signature_pending:
            return {'checked': 0, 'message': 'No pending signatures'}

        from .signature_service import check_signature_status as check_sig_status, download_signed_document

        for req in signature_pending:
            results['checked'] += 1
            try:
                sor_id = req['id']
                sig_id = req['signature_request_id']
                learner_name = req['learner_name']
                learner_id = req.get('learner_id')

                # Check signature status
                is_signed = check_sig_status(sig_id)

                if is_signed:
                    # Download signed document
                    pdf_path = req.get('pdf_path', '')
                    signed_pdf_path = pdf_path.replace(".pdf", "_SIGNED.pdf") if pdf_path else None

                    if signed_pdf_path and download_signed_document(sig_id, signed_pdf_path):
                        dashboard_db.update_sor_request(sor_id, {
                            'status': 'signed',
                            'signed_pdf_path': signed_pdf_path
                        })
                        dashboard_db.log_action(sor_id, 'signature_completed', 'Document signed and downloaded', 'success')
                        results['completed'] += 1

                        # Auto-upload to Moodle after signature
                        if learner_id:
                            try:
                                upload_result = upload_to_assignment_direct(
                                    signed_pdf_path,
                                    learner_name,
                                    learner_id,
                                    config.ASSIGNMENT_COURSEMODULE_ID
                                )
                                if upload_result:
                                    dashboard_db.update_sor_request(sor_id, {'status': 'uploaded'})
                                    dashboard_db.log_action(sor_id, 'uploaded', 'Uploaded to Moodle after signature', 'success')
                                    results['uploaded'] += 1
                            except Exception as upload_err:
                                dashboard_db.log_action(sor_id, 'upload_error', str(upload_err), 'failed')
                    else:
                        results['errors'].append(f"ID {sor_id}: Failed to download signed document")
                else:
                    results['pending'] += 1

            except Exception as e:
                results['errors'].append(f"ID {req.get('id', '?')}: {str(e)}")

        return results

    except Exception as e:
        return {'error': str(e)}


if __name__ == "__main__":
    main()