"""
Debug script to check what score is being returned from the database
"""
from src.database import db
from src.config import config

learner_name = config.TEST_LEARNER_NAME
print(f"Fetching data for: {learner_name}")
print("=" * 60)

learner_data = db.fetch_all_learner_data(learner_name)

if learner_data:
    print("Learner data keys:", learner_data.keys())
    print("\nOverall score:", learner_data.get('overall_score'))
    print("Type:", type(learner_data.get('overall_score')))

    # Check if it exists in the data
    if 'overall_score' in learner_data:
        print(f"✓ 'overall_score' EXISTS in data: {learner_data['overall_score']}")
    else:
        print("✗ 'overall_score' does NOT exist in data")

    print("\n" + "=" * 60)
    print("Full learner_data structure:")
    print("=" * 60)
    import json
    print(json.dumps(learner_data, indent=2, default=str))
else:
    print("[X] No learner data found")

input("\nPress Enter to exit...")
