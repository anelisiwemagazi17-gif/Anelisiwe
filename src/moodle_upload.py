"""
Moodle upload module for SOR Automation System
Handles uploading signed PDFs to Moodle assignments
"""
from .config import config
import requests
import pymysql
import time
import hashlib
import os

def upload_to_assignment_direct(file_path: str, learner_name: str, learner_id: int, course_module_id: int):
    """
    Upload file to Moodle assignment using direct DB manipulation.
    Returns dictionary with upload info if successful.
    """
    try:
        # Get assignment ID
        conn = pymysql.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            port=config.DB_PORT,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cur:
            cur.execute("SELECT a.id as assign_id, a.name as assignment_name FROM mdl_assign a JOIN mdl_course_modules cm ON cm.instance = a.id WHERE cm.id = %s LIMIT 1", (course_module_id,))
            result = cur.fetchone()
            if not result:
                print(f"No assignment found for coursemodule {course_module_id}")
                return None
            assign_id = result['assign_id']
            assignment_name = result['assignment_name']

        # Create filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"SOR_{learner_name.replace(' ', '_')}_{timestamp}.pdf"

        # Upload to draft
        draft_itemid = upload_file_to_moodle(file_path, filename)
        if not draft_itemid:
            return None

        # Submit via web service
        submission_data = {
            'assignmentid': assign_id,
            'userid': learner_id,
            'plugindata[files_filemanager]': draft_itemid,
            'plugindata[assignsubmission_file_filemanager]': draft_itemid,
        }

        result = moodle_ws_call('mod_assign_save_submission', submission_data)
        if result:
            print(f"Web service submission successful")
            return {
                'filename': filename,
                'assignment_id': assign_id,
                'coursemodule_id': course_module_id,
                'assignment_name': assignment_name,
                'method': 'web_service'
            }
        else:
            print(f"Web service failed, using manual method")
            return upload_to_assignment_manual(file_path, filename, learner_id, assign_id, course_module_id)

    except Exception as e:
        print(f"Upload error: {e}")
        return None
    finally:
        conn.close()

def upload_file_to_moodle(file_path: str, filename: str):
    """Upload a file to Moodle's draft area"""
    upload_url = f"{config.MOODLE_URL}/webservice/upload.php"
    try:
        with open(file_path, 'rb') as f:
            files = {
                'file_1': (filename, f, 'application/pdf')
            }
            data = {
                'token': config.MOODLE_TOKEN,
                'filearea': 'draft',
                'itemid': 0
            }
            response = requests.post(upload_url, files=files, data=data, timeout=60)
            if response.status_code == 200:
                result = response.json()
                if result and len(result) > 0 and 'itemid' in result[0]:
                    return result[0]['itemid']
            print(f"Upload failed: {response.text[:200]}")
    except Exception as e:
        print(f"Upload error: {e}")
    return None

def moodle_ws_call(function: str, params: dict):
    """Make a Moodle web service call"""
    ws_url = f"{config.MOODLE_URL}/webservice/rest/server.php"
    data = {
        'wstoken': config.MOODLE_TOKEN,
        'wsfunction': function,
        'moodlewsrestformat': 'json'
    }
    data.update(params)
    try:
        response = requests.post(ws_url, data=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict) and 'exception' in result:
                print(f"Moodle error: {result.get('message', 'Unknown error')}")
                return None
            return result
        print(f"HTTP error: {response.text[:200]}")
        return None
    except Exception as e:
        print(f"Request error: {e}")
        return None

def upload_to_assignment_manual(file_path: str, filename: str, user_id: int, assign_id: int, coursemodule_id: int):
    """Manual upload method"""
    conn = pymysql.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        port=config.DB_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with conn.cursor() as cur:
            current_time = int(time.time())

            # Check existing submission
            cur.execute("SELECT id FROM mdl_assign_submission WHERE assignment = %s AND userid = %s LIMIT 1", (assign_id, user_id))
            existing = cur.fetchone()
            if existing:
                submission_id = existing['id']
            else:
                cur.execute("INSERT INTO mdl_assign_submission (assignment, userid, timecreated, timemodified, status, attemptnumber, latest) VALUES (%s, %s, %s, %s, 'submitted', 0, 1)", (assign_id, user_id, current_time, current_time))
                submission_id = cur.lastrowid

            # Get context
            cur.execute("SELECT ctx.id as contextid FROM mdl_context ctx JOIN mdl_course_modules cm ON ctx.instanceid = cm.id WHERE cm.id = %s AND ctx.contextlevel = 70 LIMIT 1", (coursemodule_id,))
            context = cur.fetchone()
            if not context:
                return None
            context_id = context['contextid']

            # Read file
            with open(file_path, 'rb') as f:
                file_content = f.read()
            contenthash = hashlib.sha1(file_content).hexdigest()
            filesize = len(file_content)
            filepath = "/"
            pathname = f"/{context_id}/assignsubmission_file/submission_files/{submission_id}{filepath}{filename}"
            pathnamehash = hashlib.sha1(pathname.encode()).hexdigest()

            # Delete existing file
            cur.execute("DELETE FROM mdl_files WHERE component = 'assignsubmission_file' AND filearea = 'submission_files' AND itemid = %s", (submission_id,))

            # Insert file record
            cur.execute("INSERT INTO mdl_files (contenthash, pathnamehash, contextid, component, filearea, itemid, filepath, filename, userid, filesize, mimetype, status, source, author, license, timecreated, timemodified, sortorder) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (
                contenthash, pathnamehash, context_id, 'assignsubmission_file', 'submission_files',
                submission_id, filepath, filename, user_id, filesize, 'application/pdf',
                0, filename, f"SOR Automation", 'allrightsreserved', current_time, current_time, 0
            ))

            # Update assignsubmission_file
            cur.execute("DELETE FROM mdl_assignsubmission_file WHERE assignment = %s AND submission = %s", (assign_id, submission_id))
            cur.execute("INSERT INTO mdl_assignsubmission_file (assignment, submission, numfiles) VALUES (%s, %s, 1)", (assign_id, submission_id))

            # Update submission
            cur.execute("UPDATE mdl_assign_submission SET timemodified = %s WHERE id = %s", (current_time, submission_id))

            conn.commit()
            return {
                'filename': filename,
                'submission_id': submission_id,
                'file_id': cur.lastrowid,
                'context_id': context_id,
                'assignment_id': assign_id,
                'coursemodule_id': coursemodule_id,
                'method': 'manual'
            }

    except Exception as e:
        conn.rollback()
        print(f"Manual upload error: {e}")
        return None
    finally:
        conn.close()