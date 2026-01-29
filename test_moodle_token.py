"""
Quick test script to verify Moodle token
Run this before updating .env file
"""
import requests

def test_token(token):
    """Test if a Moodle token is valid"""
    print("=" * 60)
    print("Testing Moodle Token")
    print("=" * 60)

    url = "https://lms.mindworx.co.za/academy/webservice/rest/server.php"

    data = {
        'wstoken': token,
        'wsfunction': 'core_webservice_get_site_info',
        'moodlewsrestformat': 'json'
    }

    try:
        print(f"\nTesting token: {token[:10]}...")
        response = requests.post(url, data=data, timeout=10)

        if response.status_code == 200:
            result = response.json()

            if 'exception' in result:
                print(f"\n❌ INVALID TOKEN!")
                print(f"   Error: {result.get('message', 'Unknown error')}")
                return False
            elif 'sitename' in result:
                print(f"\n✅ TOKEN IS VALID!")
                print(f"   Site: {result['sitename']}")
                print(f"   User: {result.get('firstname', '')} {result.get('lastname', '')}")
                print(f"   User ID: {result.get('userid', 'N/A')}")
                return True
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            return False

    except Exception as e:
        print(f"\n❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    print("\nPaste your new Moodle token here:")
    print("(You can get it from Moodle → Profile → Preferences → Security keys)")
    print()

    new_token = input("Token: ").strip()

    if test_token(new_token):
        print("\n" + "=" * 60)
        print("SUCCESS! Your token works.")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Open the .env file")
        print("2. Find the line: MOODLE_TOKEN=...")
        print("3. Replace the old token with this new one:")
        print(f"   MOODLE_TOKEN={new_token}")
        print("4. Save the .env file")
        print("5. Restart the dashboard")
    else:
        print("\n" + "=" * 60)
        print("FAILED! Token is not valid.")
        print("=" * 60)
        print("\nPlease:")
        print("1. Log into Moodle")
        print("2. Go to Profile → Preferences → Security keys")
        print("3. Create a new token or copy an existing valid one")
        print("4. Run this script again")

    input("\nPress Enter to exit...")
