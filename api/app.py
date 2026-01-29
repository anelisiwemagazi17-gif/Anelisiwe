"""
MindWorx SOR Automation - Flask API Backend
Connects Python logic to Next.js frontend
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dashboard_db import dashboard_db
from src.moodle_service import moodle_service
from src.config import config

app = Flask(__name__)
CORS(app)  # Enable CORS for Next.js frontend

# ===== Dashboard Stats =====

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        stats = dashboard_db.get_dashboard_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ===== SOR Requests =====

@app.route('/api/requests', methods=['GET'])
def get_requests():
    """Get all SOR requests with optional filtering"""
    try:
        status = request.args.get('status', None)
        search = request.args.get('search', None)
        limit = request.args.get('limit', 100, type=int)

        requests_data = dashboard_db.get_all_sor_requests(limit=limit)

        # Apply filters
        if status and status != 'all':
            requests_data = [r for r in requests_data if r['status'] == status]

        if search:
            search_lower = search.lower()
            requests_data = [r for r in requests_data if
                search_lower in r['learner_name'].lower() or
                search_lower in (r.get('learner_email') or '').lower()]

        # Format for JSON
        formatted = []
        for req in requests_data:
            formatted.append({
                'id': req['id'],
                'learner_name': req['learner_name'],
                'learner_email': req.get('learner_email', ''),
                'learner_id': req.get('learner_id'),
                'status': req['status'],
                'overall_score': float(req['overall_score']) if req.get('overall_score') else None,
                'pdf_path': req.get('pdf_path'),
                'signature_request_id': req.get('signature_request_id'),
                'created_at': req['created_at'].isoformat() if req['created_at'] else None,
                'updated_at': req['updated_at'].isoformat() if req['updated_at'] else None,
            })

        return jsonify({
            'success': True,
            'data': formatted,
            'count': len(formatted)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/requests', methods=['POST'])
def create_request():
    """Create a new SOR request and automatically process the full workflow"""
    try:
        from src.database import db
        from src.pdf_generator import generate_sor_pdf
        from src.signature_service import signature_service
        from src.moodle_upload import upload_to_assignment_direct

        data = request.get_json() or {}
        learner_name = data.get('learner_name')
        learner_email = data.get('learner_email')
        learner_id = data.get('learner_id')
        auto_process = data.get('auto_process', True)  # Default to auto-process

        if not learner_name or not learner_id:
            return jsonify({'success': False, 'error': 'Learner name and Moodle User ID are required'}), 400

        # Fetch quiz results from Moodle database
        results = db.fetch_results(learner_name)

        if not results:
            return jsonify({
                'success': False,
                'error': f'No quiz results found for "{learner_name}". Make sure the learner has completed the required quizzes.'
            }), 400

        # Calculate overall score using weights from config
        total_weighted_score = 0
        total_weight = 0

        for result in results:
            quiz_id = result['quiz_id']
            if quiz_id in config.QUIZ_WEIGHTS:
                weight = config.QUIZ_WEIGHTS[quiz_id]
                total_marks = float(result['total_marks']) if result['total_marks'] else 0
                learner_score = float(result['learner_score']) if result['learner_score'] else 0
                if total_marks > 0:
                    percentage = (learner_score / total_marks) * 100
                    total_weighted_score += percentage * weight
                    total_weight += weight

        overall_score = round(total_weighted_score / total_weight, 2) if total_weight > 0 else 0

        # Create the SOR request in dashboard database
        sor_id = dashboard_db.create_sor_request(
            learner_id=int(learner_id),
            learner_name=learner_name,
            learner_email=learner_email or '',
            overall_score=overall_score
        )

        if not sor_id:
            return jsonify({'success': False, 'error': 'Failed to create SOR request'}), 500

        dashboard_db.log_action(sor_id, 'request_created', f'SOR request created with score: {overall_score}%', 'success')

        workflow_status = {
            'request_created': True,
            'pdf_generated': False,
            'signature_sent': False,
            'uploaded': False
        }
        error_message = None

        # Auto-process the full workflow if enabled
        if auto_process:
            # Step 1: Generate PDF
            try:
                # Fetch full learner data from Moodle database for PDF generation
                learner_data = db.fetch_all_learner_data(learner_name)

                if not learner_data:
                    raise Exception(f"Could not fetch learner data for '{learner_name}'")

                # Generate PDF output path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pdf_output_dir = os.path.join(os.path.expanduser("~"), "Downloads", "MindWorx_SOR_PDFs")
                os.makedirs(pdf_output_dir, exist_ok=True)
                pdf_output_path = os.path.join(pdf_output_dir, f"SOR_{learner_name.replace(' ', '_')}_{timestamp}.pdf")

                # Generate PDF with correct arguments
                pdf_path = generate_sor_pdf(learner_name, learner_data, pdf_output_path)

                if pdf_path:
                    dashboard_db.update_sor_request(sor_id, {'pdf_path': pdf_path, 'status': 'pdf_generated'})
                    dashboard_db.log_action(sor_id, 'pdf_generated', f'PDF generated: {pdf_path}', 'success')
                    workflow_status['pdf_generated'] = True

                    # Step 2: Send for Signature (if not skipping)
                    if not config.SKIP_SIGNATURE and learner_email:
                        try:
                            sig_result = signature_service.send_for_signature(
                                pdf_path,
                                learner_name,
                                learner_email
                            )

                            if sig_result:
                                dashboard_db.update_sor_request(sor_id, {
                                    'status': 'signature_sent',
                                    'signature_request_id': sig_result
                                })
                                dashboard_db.log_action(sor_id, 'signature_sent', f'Sent for e-signature (ID: {sig_result})', 'success')
                                workflow_status['signature_sent'] = True
                            else:
                                dashboard_db.log_action(sor_id, 'signature_failed', 'Failed to send for signature', 'failed')
                        except Exception as sig_err:
                            dashboard_db.log_action(sor_id, 'signature_error', str(sig_err), 'failed')
                    else:
                        # Skip signature - go directly to upload
                        try:
                            upload_result = upload_to_assignment_direct(
                                pdf_path,
                                learner_name,
                                int(learner_id),
                                config.ASSIGNMENT_COURSEMODULE_ID
                            )

                            if upload_result:
                                dashboard_db.update_sor_request(sor_id, {'status': 'uploaded'})
                                dashboard_db.log_action(sor_id, 'uploaded', 'Uploaded to Moodle (signature skipped)', 'success')
                                workflow_status['uploaded'] = True
                            else:
                                dashboard_db.log_action(sor_id, 'upload_failed', 'Failed to upload to Moodle', 'failed')
                        except Exception as upload_err:
                            dashboard_db.log_action(sor_id, 'upload_error', str(upload_err), 'failed')
                else:
                    dashboard_db.log_action(sor_id, 'pdf_failed', 'Failed to generate PDF', 'failed')
                    error_message = 'Failed to generate PDF'
            except Exception as pdf_err:
                dashboard_db.log_action(sor_id, 'pdf_error', str(pdf_err), 'failed')
                error_message = f'PDF generation error: {str(pdf_err)}'

        return jsonify({
            'success': True,
            'message': 'SOR request created and processing started',
            'data': {
                'id': sor_id,
                'learner_name': learner_name,
                'overall_score': overall_score,
                'quiz_count': len(results),
                'workflow_status': workflow_status,
                'error': error_message
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/learner-grades/<int:learner_id>', methods=['GET'])
def get_learner_grades(learner_id):
    """Fetch quiz grades for a learner from Moodle"""
    try:
        from src.database import db

        learner_name = request.args.get('name', '')

        if not learner_name:
            # Try to get learner name from Moodle
            user = moodle_service.get_user_by_id(learner_id)
            if user:
                learner_name = f"{user.get('firstname', '')} {user.get('lastname', '')}".strip()

        if not learner_name:
            return jsonify({'success': False, 'error': 'Could not find learner'}), 404

        # Fetch quiz results
        results = db.fetch_results(learner_name)

        if not results:
            return jsonify({
                'success': True,
                'data': {
                    'learner_name': learner_name,
                    'quizzes': [],
                    'overall_score': None,
                    'message': 'No quiz results found'
                }
            })

        # Format quiz results
        quizzes = []
        total_weighted_score = 0
        total_weight = 0

        for result in results:
            quiz_id = result['quiz_id']
            # Convert Decimal to float for calculations
            learner_score = float(result['learner_score']) if result['learner_score'] else 0
            total_marks = float(result['total_marks']) if result['total_marks'] else 0
            percentage = 0
            if total_marks > 0:
                percentage = round((learner_score / total_marks) * 100, 2)

            quizzes.append({
                'quiz_id': quiz_id,
                'topic_name': result['topic_name'],
                'score': learner_score,
                'total_marks': total_marks,
                'percentage': percentage
            })

            if quiz_id in config.QUIZ_WEIGHTS:
                weight = config.QUIZ_WEIGHTS[quiz_id]
                total_weighted_score += percentage * weight
                total_weight += weight

        overall_score = round(total_weighted_score / total_weight, 2) if total_weight > 0 else 0

        return jsonify({
            'success': True,
            'data': {
                'learner_name': learner_name,
                'quizzes': quizzes,
                'overall_score': overall_score,
                'quiz_count': len(quizzes)
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/requests/<int:request_id>', methods=['GET'])
def get_request(request_id):
    """Get a single SOR request by ID"""
    try:
        req = dashboard_db.get_sor_request(request_id)
        if not req:
            return jsonify({'success': False, 'error': 'Request not found'}), 404

        # Get audit log
        audit_log = dashboard_db.get_audit_log(request_id)

        return jsonify({
            'success': True,
            'data': {
                'id': req['id'],
                'learner_name': req['learner_name'],
                'learner_email': req.get('learner_email', ''),
                'learner_id': req.get('learner_id'),
                'status': req['status'],
                'overall_score': float(req['overall_score']) if req.get('overall_score') else None,
                'pdf_path': req.get('pdf_path'),
                'signature_request_id': req.get('signature_request_id'),
                'created_at': req['created_at'].isoformat() if req['created_at'] else None,
                'updated_at': req['updated_at'].isoformat() if req['updated_at'] else None,
                'audit_log': [{
                    'action': log['action'],
                    'details': log.get('details'),
                    'status': log['status'],
                    'created_at': log['created_at'].isoformat() if log['created_at'] else None
                } for log in audit_log]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ===== Actions =====

@app.route('/api/requests/<int:request_id>/generate-pdf', methods=['POST'])
def generate_pdf(request_id):
    """Generate PDF for a request"""
    try:
        from src.pdf_generator import generate_sor_pdf
        from src.database import db

        req = dashboard_db.get_sor_request(request_id)
        if not req:
            return jsonify({'success': False, 'error': 'Request not found'}), 404

        learner_name = req['learner_name']

        # Fetch full learner data from Moodle database for PDF generation
        learner_data = db.fetch_all_learner_data(learner_name)

        if not learner_data:
            return jsonify({'success': False, 'error': f"Could not fetch learner data for '{learner_name}'"}), 400

        # Generate PDF output path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_output_dir = os.path.join(os.path.expanduser("~"), "Downloads", "MindWorx_SOR_PDFs")
        os.makedirs(pdf_output_dir, exist_ok=True)
        pdf_output_path = os.path.join(pdf_output_dir, f"SOR_{learner_name.replace(' ', '_')}_{timestamp}.pdf")

        # Generate PDF with correct arguments
        pdf_path = generate_sor_pdf(learner_name, learner_data, pdf_output_path)

        if pdf_path:
            dashboard_db.update_sor_request(request_id, {'pdf_path': pdf_path, 'status': 'pdf_generated'})
            dashboard_db.log_action(request_id, 'pdf_generated', f'PDF generated: {pdf_path}', 'success')
            return jsonify({
                'success': True,
                'message': 'PDF generated successfully',
                'pdf_path': pdf_path
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to generate PDF'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/requests/<int:request_id>/send-signature', methods=['POST'])
def send_for_signature(request_id):
    """Send document for signature"""
    try:
        from src.signature_service import signature_service

        req = dashboard_db.get_sor_request(request_id)
        if not req:
            return jsonify({'success': False, 'error': 'Request not found'}), 404

        if not req.get('pdf_path'):
            return jsonify({'success': False, 'error': 'No PDF generated yet'}), 400

        # Send for signature
        result = signature_service.send_for_signature(
            req['pdf_path'],
            req['learner_name'],
            req.get('learner_email')
        )

        if result:
            dashboard_db.update_sor_request(request_id, {
                'status': 'signature_sent',
                'signature_request_id': result
            })
            dashboard_db.log_action(request_id, 'signature_sent', f'Sent for signature (ID: {result})', 'success')
            return jsonify({
                'success': True,
                'message': 'Sent for signature successfully',
                'signature_request_id': result
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to send for signature'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/requests/<int:request_id>/upload-moodle', methods=['POST'])
def upload_to_moodle(request_id):
    """Upload signed document to Moodle"""
    try:
        from src.moodle_upload import upload_to_assignment_direct

        req = dashboard_db.get_sor_request(request_id)
        if not req:
            return jsonify({'success': False, 'error': 'Request not found'}), 404

        if req['status'] not in ['signed', 'pdf_generated']:
            return jsonify({'success': False, 'error': 'Document not ready for upload'}), 400

        # Upload to Moodle
        result = upload_to_assignment_direct(
            req.get('pdf_path'),
            req['learner_name'],
            req.get('learner_id'),
            config.ASSIGNMENT_COURSEMODULE_ID
        )

        if result:
            dashboard_db.log_action(request_id, 'uploaded', 'Uploaded to Moodle', 'success')
            return jsonify({
                'success': True,
                'message': 'Uploaded to Moodle successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to upload to Moodle'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/requests/<int:request_id>/sync-grade', methods=['POST'])
def sync_grade(request_id):
    """Sync grade to Moodle"""
    try:
        data = request.get_json() or {}
        grade = data.get('grade')
        feedback = data.get('feedback', '')

        req = dashboard_db.get_sor_request(request_id)
        if not req:
            return jsonify({'success': False, 'error': 'Request not found'}), 404

        # Use provided grade or SOR score
        if grade is None:
            grade = req.get('overall_score')

        if grade is None:
            return jsonify({'success': False, 'error': 'No grade available'}), 400

        # Get assignment ID
        assignment_info = moodle_service.get_assignment_info(config.ASSIGNMENT_COURSEMODULE_ID)
        if not assignment_info:
            return jsonify({'success': False, 'error': 'Assignment not found'}), 404

        # Sync grade
        result = moodle_service.sync_grade_to_moodle(
            req.get('learner_id'),
            assignment_info.get('id'),
            float(grade),
            feedback
        )

        if result.get('success'):
            dashboard_db.log_action(request_id, 'grade_synced', f'Grade synced: {grade}%', 'success')
            return jsonify({
                'success': True,
                'message': f'Grade {grade}% synced to Moodle'
            })
        else:
            return jsonify({'success': False, 'error': result.get('message')}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ===== Bulk Actions =====

@app.route('/api/process-pending', methods=['POST'])
def process_pending():
    """Process all pending requests"""
    try:
        from src.main import process_pending_requests
        result = process_pending_requests()
        return jsonify({
            'success': True,
            'message': 'Processing completed',
            'result': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/check-signatures', methods=['POST'])
def check_signatures():
    """Check all pending signatures"""
    try:
        from src.main import check_signature_status
        result = check_signature_status()
        return jsonify({
            'success': True,
            'message': 'Signature check completed',
            'result': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/bulk-sync-grades', methods=['POST'])
def bulk_sync_grades():
    """Sync all grades to Moodle"""
    try:
        requests_data = dashboard_db.get_all_sor_requests(limit=1000)
        uploaded = [r for r in requests_data if r['status'] == 'uploaded' and r.get('overall_score')]

        if not uploaded:
            return jsonify({'success': True, 'message': 'No grades to sync', 'synced': 0})

        assignment_info = moodle_service.get_assignment_info(config.ASSIGNMENT_COURSEMODULE_ID)
        if not assignment_info:
            return jsonify({'success': False, 'error': 'Assignment not found'}), 404

        grades = [{'userid': r['learner_id'], 'grade': float(r['overall_score'])} for r in uploaded]
        result = moodle_service.bulk_grade_submissions(assignment_info.get('id'), grades)

        return jsonify({
            'success': True,
            'message': f"Synced {result['success_count']}/{result['total_processed']} grades",
            'result': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ===== System Info =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '3.0'
    })


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get system configuration (non-sensitive)"""
    return jsonify({
        'success': True,
        'data': {
            'moodle_url': config.MOODLE_URL,
            'assignment_id': config.ASSIGNMENT_COURSEMODULE_ID,
            'course_name': 'Occupational Certificate: Software Engineer 119458'
        }
    })


if __name__ == '__main__':
    print("=" * 60)
    print("MindWorx SOR Automation API")
    print("=" * 60)
    print(f"Starting server on http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, port=5000)
