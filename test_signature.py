"""
Test Dropbox Sign API Connection
Debug signature service issues
"""
from src.config import config
from requests.auth import HTTPBasicAuth
import requests

def test_api_key():
    """Test if API key is valid"""
    print("=" * 60)
    print("Testing Dropbox Sign API Key")
    print("=" * 60)

    url = "https://api.hellosign.com/v3/account"
    auth = HTTPBasicAuth(config.DROPBOX_SIGN_API_KEY, '')

    try:
        response = requests.get(url, auth=auth, timeout=10)

        if response.status_code == 200:
            result = response.json()
            account = result.get('account', {})
            print("\n✅ API Key is VALID!")
            print(f"   Email: {account.get('email_address', 'N/A')}")
            print(f"   Account ID: {account.get('account_id', 'N/A')}")
            print(f"   Quota: {account.get('quota', {}).get('documents_left', 'N/A')} documents left")
            print(f"   Templates: {account.get('quota', {}).get('templates_left', 'N/A')} templates left")
            return True
        elif response.status_code == 401:
            print("\n❌ API Key is INVALID")
            print("   Error: Unauthorized")
            print("   Please check your DROPBOX_SIGN_API_KEY in .env file")
            return False
        else:
            print(f"\n❌ API Request Failed")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"\n❌ Connection Error: {e}")
        return False

def test_learner_email():
    """Check if test learner has a valid email"""
    print("\n" + "=" * 60)
    print("Checking Test Learner Email")
    print("=" * 60)

    from src.database import db

    learner_data = db.fetch_all_learner_data(config.TEST_LEARNER_NAME)

    if not learner_data:
        print(f"\n❌ Learner not found: {config.TEST_LEARNER_NAME}")
        return False

    learner_email = learner_data['learner'].get('email')
    learner_id = learner_data['learner'].get('id')

    print(f"\n✅ Learner Found:")
    print(f"   Name: {config.TEST_LEARNER_NAME}")
    print(f"   Email: {learner_email or 'NOT SET'}")
    print(f"   ID: {learner_id}")

    if not learner_email or learner_email == 'N/A':
        print(f"\n⚠️  WARNING: Learner has no email address!")
        print(f"   This will cause signature requests to fail.")
        print(f"   Please update the learner's email in the database.")
        return False

    # Basic email validation
    if '@' not in learner_email or '.' not in learner_email:
        print(f"\n⚠️  WARNING: Email appears invalid: {learner_email}")
        return False

    print(f"\n✅ Email looks valid!")
    return True

def test_signature_request_minimal():
    """Test a minimal signature request to see exact error"""
    print("\n" + "=" * 60)
    print("Testing Minimal Signature Request")
    print("=" * 60)

    from src.database import db

    learner_data = db.fetch_all_learner_data(config.TEST_LEARNER_NAME)
    if not learner_data:
        print("❌ Cannot test - learner not found")
        return False

    learner_email = learner_data['learner'].get('email', 'test@example.com')
    learner_name = config.TEST_LEARNER_NAME

    # Find a PDF file to test with
    import os
    from pathlib import Path
    pdf_dir = Path.home() / "Downloads" / "MindWorx_SOR_PDFs"
    pdf_files = list(pdf_dir.glob("*.pdf"))

    if not pdf_files:
        print("❌ No PDF files found to test with")
        print(f"   Please run: python -m src.main  (with SKIP_SIGNATURE=true)")
        print(f"   Then run this test again")
        return False

    test_pdf = str(pdf_files[0])
    print(f"\nUsing test PDF: {os.path.basename(test_pdf)}")
    print(f"Sending to: {learner_email}")

    url = "https://api.hellosign.com/v3/signature_request/send"
    auth = HTTPBasicAuth(config.DROPBOX_SIGN_API_KEY, '')

    try:
        with open(test_pdf, 'rb') as f:
            files = {
                'file[0]': (os.path.basename(test_pdf), f, 'application/pdf')
            }

            data = {
                'title': 'Test Signature Request',
                'subject': 'Test',
                'message': 'This is a test',
                'signers[0][email_address]': learner_email,
                'signers[0][name]': learner_name,
                'test_mode': 1,  # Test mode
            }

            print("\nSending request...")
            response = requests.post(url, auth=auth, files=files, data=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                sig_id = result.get('signature_request', {}).get('signature_request_id')
                print(f"\n✅ SUCCESS!")
                print(f"   Signature Request ID: {sig_id}")
                print(f"   The signature email has been sent to: {learner_email}")
                return True
            else:
                print(f"\n❌ REQUEST FAILED")
                print(f"   Status Code: {response.status_code}")
                print(f"   Response: {response.text}")

                # Parse error details
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error = error_data['error']
                        print(f"\n   Error Name: {error.get('error_name', 'N/A')}")
                        print(f"   Error Message: {error.get('error_msg', 'N/A')}")
                except:
                    pass

                return False

    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        # Test 1: Check API key
        api_valid = test_api_key()

        if not api_valid:
            print("\n" + "=" * 60)
            print("RECOMMENDATION: Fix API key before continuing")
            print("=" * 60)
            input("\nPress Enter to exit...")
            exit(1)

        # Test 2: Check learner email
        email_valid = test_learner_email()

        # Test 3: Try actual signature request
        if email_valid:
            test_signature_request_minimal()

        print("\n" + "=" * 60)
        print("Test Complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to exit...")
