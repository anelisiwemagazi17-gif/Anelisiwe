"""
Test Moodle API Connection
Quick test to verify Moodle integration is working
"""
from src.moodle_service import moodle_service
from src.config import config

def test_moodle_connection():
    """Test Moodle API connection"""
    print("=" * 60)
    print("Testing Moodle API Connection")
    print("=" * 60)

    # Test connection
    print("\n1. Testing basic connection...")
    if moodle_service.test_connection():
        print("   ✅ Moodle API connection successful!")
    else:
        print("   ❌ Moodle API connection failed!")
        return

    # Get assignment info
    print(f"\n2. Getting assignment info (ID: {config.ASSIGNMENT_COURSEMODULE_ID})...")
    assignment = moodle_service.get_assignment_info(config.ASSIGNMENT_COURSEMODULE_ID)
    if assignment:
        print(f"   ✅ Assignment found:")
        print(f"      Name: {assignment.get('name')}")
        print(f"      ID: {assignment.get('id')}")
        print(f"      Course Module ID: {assignment.get('cmid')}")
        assignment_id = assignment.get('id')
    else:
        print("   ⚠️  Assignment not found or error occurred")
        return

    # Get submissions
    print(f"\n3. Getting submissions for assignment...")
    submissions = moodle_service.get_submissions(assignment_id)
    if submissions:
        print(f"   ✅ Found {len(submissions)} submission(s)")
        if len(submissions) > 0:
            print(f"\n   First few submissions:")
            for i, sub in enumerate(submissions[:3]):
                print(f"   - User ID: {sub.get('userid')}, Status: {sub.get('status')}")
    else:
        print("   ⚠️  No submissions found or error occurred")

    # Test verification for a specific learner
    print(f"\n4. Testing submission verification...")
    test_learner = config.TEST_LEARNER_NAME
    print(f"   Looking for: {test_learner}")

    result = moodle_service.verify_submission(test_learner, assignment_id)
    if result['found']:
        print(f"   ✅ {result['message']}")
        print(f"   Status: {result['status']}")
        if result.get('timemodified'):
            from datetime import datetime
            modified_time = datetime.fromtimestamp(result['timemodified'])
            print(f"   Last Modified: {modified_time}")
    else:
        print(f"   ℹ️  {result['message']}")

    # Generate Moodle URLs
    print(f"\n5. Moodle URLs:")
    print(f"   Assignment URL: {moodle_service.get_moodle_url_for_assignment(config.ASSIGNMENT_COURSEMODULE_ID)}")

    print("\n" + "=" * 60)
    print("Moodle API Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_moodle_connection()
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to exit...")
