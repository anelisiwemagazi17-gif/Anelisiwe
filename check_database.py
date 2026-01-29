"""
Quick database checker to see what fields are available
"""
from src.config import config
from src.database import db

print("=" * 60)
print("DATABASE FIELD CHECKER")
print("=" * 60)

# Test connection
if not db.test_connection():
    print("Failed to connect to database")
    exit(1)

# Check learner
learner_name = config.TEST_LEARNER_NAME
print(f"\nLooking for learner: {learner_name}")

learner = db.fetch_learner_by_name(learner_name)
if not learner:
    print(f"❌ Learner '{learner_name}' not found in database")
    exit(1)

print(f"✅ Found learner: {learner}")

# Check profile fields
user_id = learner['id']
profile = db.fetch_user_info_data(user_id)

print(f"\n" + "=" * 60)
print("AVAILABLE PROFILE FIELDS")
print("=" * 60)
if profile:
    for field_name, value in profile.items():
        print(f"  {field_name}: {value}")
else:
    print("  No profile fields found")

print("\n" + "=" * 60)
print("REQUIRED FIELDS (from validation.py)")
print("=" * 60)
required = ["Registration Number", "Date of Birth", "Learner Number"]
for field in required:
    status = "✅" if field in profile else "❌ MISSING"
    value = profile.get(field, "N/A")
    print(f"  {status} {field}: {value}")

print("\n" + "=" * 60)
print("SUGGESTIONS")
print("=" * 60)
print("If fields are missing, check:")
print("1. Field names in mdl_user_info_field table")
print("2. Data in mdl_user_info_data table for this user")
print("3. Update validation.py to match actual field names")
print("=" * 60)
