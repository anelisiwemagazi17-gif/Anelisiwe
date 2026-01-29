"""
Moodle Service Module for Dashboard
Handles Moodle API interactions for dashboard
"""
import requests
from typing import Dict, List, Optional
from .config import config

class MoodleService:
    """Handles Moodle API calls for dashboard"""

    def __init__(self):
        self.base_url = config.MOODLE_URL
        self.token = config.MOODLE_TOKEN
        self.ws_url = f"{self.base_url}/webservice/rest/server.php"

    def _call_api(self, function: str, params: Dict = None) -> Optional[Dict]:
        """Make a Moodle web service call"""
        try:
            data = {
                'wstoken': self.token,
                'wsfunction': function,
                'moodlewsrestformat': 'json'
            }
            if params:
                data.update(params)

            response = requests.post(self.ws_url, data=data, timeout=30)

            if response.status_code == 200:
                result = response.json()

                # Check for errors
                if isinstance(result, dict) and 'exception' in result:
                    print(f"❌ Moodle API error: {result.get('message', 'Unknown error')}")
                    return None

                return result
            else:
                print(f"❌ HTTP error {response.status_code}: {response.text[:200]}")
                return None

        except Exception as e:
            print(f"❌ Moodle API call failed: {e}")
            return None

    # ===== Assignment Functions =====

    def get_assignment_info(self, course_module_id: int) -> Optional[Dict]:
        """Get assignment information"""
        result = self._call_api('mod_assign_get_assignments', {
            'courseids[0]': 8  # Course ID
        })

        if result and 'courses' in result:
            for course in result['courses']:
                for assignment in course.get('assignments', []):
                    if assignment.get('cmid') == course_module_id:
                        return assignment
        return None

    def get_submissions(self, assignment_id: int) -> Optional[List[Dict]]:
        """Get all submissions for an assignment"""
        result = self._call_api('mod_assign_get_submissions', {
            'assignmentids[0]': assignment_id
        })

        if result and 'assignments' in result:
            for assignment in result['assignments']:
                return assignment.get('submissions', [])
        return None

    def get_submission_status(self, assignment_id: int, user_id: int) -> Optional[Dict]:
        """Get submission status for a specific user"""
        result = self._call_api('mod_assign_get_submission_status', {
            'assignid': assignment_id,
            'userid': user_id
        })
        return result

    def verify_submission(self, learner_name: str, coursemodule_id: int, learner_id: int = None) -> Dict:
        """Verify if learner has submitted to assignment

        Args:
            learner_name: Name of the learner
            coursemodule_id: Course module ID (cmid) from Moodle URL
            learner_id: Optional learner ID from database
        """
        try:
            # First, get the assignment info to convert cmid to assignment ID
            assignment_info = self.get_assignment_info(coursemodule_id)

            if not assignment_info:
                return {
                    'found': False,
                    'status': 'Assignment not found',
                    'message': f'Could not find assignment with course module ID {coursemodule_id}'
                }

            assignment_id = assignment_info.get('id')
            submissions = self.get_submissions(assignment_id)

            if not submissions:
                return {
                    'found': False,
                    'status': 'No submissions found',
                    'message': f'Could not retrieve submissions from Moodle (Assignment ID: {assignment_id})'
                }

            # If we have learner_id from database, use it directly
            if learner_id:
                for submission in submissions:
                    if submission.get('userid') == learner_id:
                        return {
                            'found': True,
                            'status': submission.get('status', 'Unknown'),
                            'timemodified': submission.get('timemodified'),
                            'userid': learner_id,
                            'message': f"Submission found - Status: {submission.get('status', 'Unknown')}"
                        }

                return {
                    'found': False,
                    'status': 'Not submitted',
                    'message': f'No submission found for user ID {learner_id}'
                }

            # Fallback: Use database to get user ID by name
            from .database import db
            learner = db.fetch_learner_by_name(learner_name)

            if learner:
                user_id = learner['id']
                for submission in submissions:
                    if submission.get('userid') == user_id:
                        return {
                            'found': True,
                            'status': submission.get('status', 'Unknown'),
                            'timemodified': submission.get('timemodified'),
                            'userid': user_id,
                            'message': f"Submission found - Status: {submission.get('status', 'Unknown')}"
                        }

            return {
                'found': False,
                'status': 'Not submitted',
                'message': f'No submission found for {learner_name}'
            }

        except Exception as e:
            return {
                'found': False,
                'status': 'Error',
                'message': f'Error checking submission: {e}'
            }

    # ===== User Functions =====

    def get_user_by_name(self, firstname: str, lastname: str) -> Optional[Dict]:
        """Get user by first and last name"""
        result = self._call_api('core_user_get_users', {
            'criteria[0][key]': 'firstname',
            'criteria[0][value]': firstname,
            'criteria[1][key]': 'lastname',
            'criteria[1][value]': lastname
        })

        if result and 'users' in result and result['users']:
            return result['users'][0]
        return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        result = self._call_api('core_user_get_users', {
            'criteria[0][key]': 'id',
            'criteria[0][value]': user_id
        })

        if result and 'users' in result and result['users']:
            return result['users'][0]
        return None

    # ===== Course Functions =====

    def get_course_contents(self, course_id: int) -> Optional[List[Dict]]:
        """Get course contents"""
        result = self._call_api('core_course_get_contents', {
            'courseid': course_id
        })
        return result if result else None

    # ===== Utility Functions =====

    def test_connection(self) -> bool:
        """Test Moodle API connection"""
        try:
            result = self._call_api('core_webservice_get_site_info')
            if result and 'sitename' in result:
                print(f"✅ Connected to Moodle: {result['sitename']}")
                return True
            return False
        except Exception as e:
            print(f"❌ Moodle connection failed: {e}")
            return False

    def get_moodle_url_for_assignment(self, course_module_id: int) -> str:
        """Get direct URL to assignment in Moodle"""
        return f"{self.base_url}/mod/assign/view.php?id={course_module_id}"

    def get_moodle_url_for_submission(self, course_module_id: int, user_id: int = None) -> str:
        """Get direct URL to view submission"""
        url = f"{self.base_url}/mod/assign/view.php?id={course_module_id}&action=grading"
        if user_id:
            url += f"&userid={user_id}"
        return url

    # ===== Grading Functions =====

    def grade_submission(self, assignment_id: int, user_id: int, grade: float,
                        feedback: str = '', attempt_number: int = -1) -> Dict:
        """
        Grade a single submission

        Args:
            assignment_id: Assignment ID
            user_id: User ID
            grade: Grade percentage (0-100)
            feedback: Optional feedback text
            attempt_number: Attempt number (-1 for latest)

        Returns:
            Dict with success status and details
        """
        try:
            # First try the local_sor plugin API
            result = self._call_api('local_sor_grade_submission', {
                'assignmentid': assignment_id,
                'userid': user_id,
                'grade': grade,
                'feedback': feedback,
                'attemptnumber': attempt_number
            })

            if result and 'success' in result:
                return result

            # Fallback to standard Moodle API
            result = self._call_api('mod_assign_save_grade', {
                'assignmentid': assignment_id,
                'userid': user_id,
                'grade': grade,
                'attemptnumber': attempt_number,
                'addattempt': 0,
                'workflowstate': 'released',
                'applytoall': 0,
                'plugindata[assignfeedbackcomments_editor][text]': feedback,
                'plugindata[assignfeedbackcomments_editor][format]': 1
            })

            if result is None or (isinstance(result, list) and len(result) == 0):
                return {
                    'success': True,
                    'message': f'Grade {grade}% saved for user {user_id}'
                }

            return {
                'success': False,
                'message': f'Failed to save grade: {result}'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Grading error: {e}'
            }

    def bulk_grade_submissions(self, assignment_id: int, grades: List[Dict]) -> Dict:
        """
        Grade multiple submissions at once

        Args:
            assignment_id: Assignment ID
            grades: List of dicts with 'userid', 'grade', and optional 'feedback'

        Returns:
            Dict with overall success status and individual results
        """
        results = []
        success_count = 0
        fail_count = 0

        for grade_data in grades:
            result = self.grade_submission(
                assignment_id,
                grade_data['userid'],
                grade_data['grade'],
                grade_data.get('feedback', '')
            )

            if result.get('success'):
                success_count += 1
            else:
                fail_count += 1

            results.append({
                'userid': grade_data['userid'],
                'success': result.get('success', False),
                'message': result.get('message', '')
            })

        return {
            'success': fail_count == 0,
            'total_processed': len(grades),
            'success_count': success_count,
            'fail_count': fail_count,
            'results': results
        }

    def get_grading_status(self, assignment_id: int) -> Dict:
        """
        Get grading status for an assignment

        Returns:
            Dict with graded/ungraded counts and details
        """
        try:
            # Try local_sor plugin first
            result = self._call_api('local_sor_get_grading_status', {
                'assignmentid': assignment_id
            })

            if result and 'totalsubmissions' in result:
                return result

            # Fallback: calculate from submissions
            submissions = self.get_submissions(assignment_id)
            if not submissions:
                return {
                    'totalsubmissions': 0,
                    'graded': 0,
                    'ungraded': 0,
                    'percentagegraded': 0
                }

            total = len(submissions)
            graded = sum(1 for s in submissions if s.get('gradingstatus') == 'graded')

            return {
                'totalsubmissions': total,
                'graded': graded,
                'ungraded': total - graded,
                'percentagegraded': round((graded / total) * 100, 1) if total > 0 else 0
            }

        except Exception as e:
            print(f"❌ Error getting grading status: {e}")
            return {
                'totalsubmissions': 0,
                'graded': 0,
                'ungraded': 0,
                'percentagegraded': 0,
                'error': str(e)
            }

    def get_grades(self, assignment_id: int) -> Optional[List[Dict]]:
        """Get all grades for an assignment"""
        result = self._call_api('mod_assign_get_grades', {
            'assignmentids[0]': assignment_id
        })

        if result and 'assignments' in result:
            for assignment in result['assignments']:
                if assignment.get('assignmentid') == assignment_id:
                    return assignment.get('grades', [])
        return None

    def get_user_grade(self, assignment_id: int, user_id: int) -> Optional[Dict]:
        """Get grade for a specific user"""
        grades = self.get_grades(assignment_id)
        if grades:
            for grade in grades:
                if grade.get('userid') == user_id:
                    return grade
        return None

    def release_grades(self, assignment_id: int, user_ids: List[int] = None) -> Dict:
        """
        Release grades to students (for marking workflow)

        Args:
            assignment_id: Assignment ID
            user_ids: List of user IDs to release (None for all)

        Returns:
            Dict with success status
        """
        try:
            params = {'assignmentid': assignment_id}
            if user_ids:
                for i, uid in enumerate(user_ids):
                    params[f'userids[{i}]'] = uid

            result = self._call_api('local_sor_release_grades', params)

            if result and 'success' in result:
                return result

            return {
                'success': False,
                'message': 'Failed to release grades'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error releasing grades: {e}'
            }

    def sync_grade_to_moodle(self, learner_id: int, assignment_id: int, score: float,
                             feedback: str = None) -> Dict:
        """
        Sync a grade from the SOR system to Moodle

        Args:
            learner_id: Moodle user ID
            assignment_id: Moodle assignment ID
            score: Score percentage
            feedback: Optional feedback

        Returns:
            Dict with sync result
        """
        if feedback is None:
            feedback = f"SOR Assessment completed. Score: {score:.2f}%"

        result = self.grade_submission(assignment_id, learner_id, score, feedback)

        if result.get('success'):
            print(f"✅ Grade synced to Moodle: User {learner_id} = {score}%")
        else:
            print(f"❌ Failed to sync grade: {result.get('message')}")

        return result


# Create Moodle service instance
moodle_service = MoodleService()
