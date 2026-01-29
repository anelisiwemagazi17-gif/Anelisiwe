"""
Signature service module for SOR Automation System
Handles Dropbox Sign API interactions
"""
from requests.auth import HTTPBasicAuth
import requests
import time
import os
from .config import config

def send_signature_request(pdf_path: str, learner_email: str, learner_name: str):
    """
    Sends PDF to Dropbox Sign for signature.
    Returns signature request ID if successful.
    """
    file_handle = None
    try:
        url = "https://api.hellosign.com/v3/signature_request/send"
        auth = HTTPBasicAuth(config.DROPBOX_SIGN_API_KEY, '')

        file_handle = open(pdf_path, 'rb')
        files = {
            'file[0]': (
                os.path.basename(pdf_path),
                file_handle,
                'application/pdf'
            )
        }

        data = {
            'title': 'MindWorx Statement of Results - Signature Required',
            'subject': 'Please sign your Statement of Results',
            'message': f'Dear {learner_name},\n\nPlease review and sign your MindWorx Statement of Results.',
            'signers[0][email_address]': learner_email,
            'signers[0][name]': learner_name,
            'test_mode': 1,  # Set to 1 for test mode (free), 0 for production (requires paid account)
        }

        response = requests.post(url, auth=auth, files=files, data=data)
        response.raise_for_status()
        result = response.json()

        if 'signature_request' in result:
            signature_request_id = result['signature_request']['signature_request_id']
            print("[OK] Signature request sent successfully!")
            print(f"   Signature Request ID: {signature_request_id}")
            return signature_request_id
        else:
            print("[X] Unexpected response format:", result)
            return None

    except Exception as e:
        print(f"[X] Failed to send signature request: {e}")
        return None
    finally:
        if file_handle:
            file_handle.close()

def wait_for_signature(signature_request_id: str, max_wait_minutes: int = 60, check_interval: int = 30):
    """
    Waits for the signature to be completed.
    Returns True if signed, False if timeout.
    """
    elapsed = 0
    print(f"[...] Waiting for signature (max {max_wait_minutes} minutes)...")
    while elapsed < max_wait_minutes * 60:
        if check_signature_status(signature_request_id):
            return True
        print(f"   Still waiting... ({elapsed // 60} min elapsed)")
        time.sleep(check_interval)
        elapsed += check_interval
    print("[TIMEOUT]  Timeout: Document not signed in time")
    return False

def check_signature_status(signature_request_id: str):
    """Check if signature request has been completed"""
    url = f"https://api.hellosign.com/v3/signature_request/{signature_request_id}"
    auth = HTTPBasicAuth(config.DROPBOX_SIGN_API_KEY, '')

    try:
        response = requests.get(url, auth=auth, timeout=15)
        response.raise_for_status()
        result = response.json()

        if 'signature_request' in result:
            sr = result['signature_request']
            is_complete = sr.get('is_complete', False)

            signatures = sr.get('signatures', [])
            for sig in signatures:
                status = sig.get('status_code')
                if status == 'signed':
                    print("[OK] Document has been signed!")
                    return True

            return is_complete

        return False

    except Exception as e:
        print(f"[X] Failed to check signature status: {e}")
        return False

def download_signed_document(signature_request_id: str, output_path: str, max_retries: int = 10, retry_delay: int = 15):
    """Download the signed PDF from Dropbox Sign"""
    url = f"https://api.hellosign.com/v3/signature_request/files/{signature_request_id}"
    auth = HTTPBasicAuth(config.DROPBOX_SIGN_API_KEY, '')
    params = {'file_type': 'pdf'}

    for attempt in range(max_retries):
        print(f"[DOWNLOAD] Attempt {attempt + 1}/{max_retries} to download signed document...")

        try:
            response = requests.get(url, auth=auth, params=params, stream=True, timeout=30)

            if response.status_code == 409:
                print("   [...] Document not ready yet. Waiting...")
                time.sleep(retry_delay)
                continue

            response.raise_for_status()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(8192):
                    if chunk:
                        f.write(chunk)

            print(f"[OK] Signed document downloaded: {output_path}")
            return True

        except Exception as e:
            print(f"   [X] Download attempt failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)

    print("[X] Failed to download signed document after all retries")
    return False


class SignatureService:
    """Wrapper class for signature functions"""

    def send_for_signature(self, pdf_path: str, learner_name: str, learner_email: str):
        """Send PDF for signature"""
        return send_signature_request(pdf_path, learner_email, learner_name)

    def check_status(self, signature_request_id: str):
        """Check signature status"""
        return check_signature_status(signature_request_id)

    def wait_for_completion(self, signature_request_id: str, max_wait_minutes: int = 60):
        """Wait for signature completion"""
        return wait_for_signature(signature_request_id, max_wait_minutes)

    def download_signed(self, signature_request_id: str, output_path: str):
        """Download signed document"""
        return download_signed_document(signature_request_id, output_path)


# Create signature service instance
signature_service = SignatureService()