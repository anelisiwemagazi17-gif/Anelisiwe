"""
Update existing SOR requests with scores from learner data
"""
from src.dashboard_db import dashboard_db
from src.database import db
from src.pdf_generator import calculate_overall_score

def update_all_scores():
    """Update all SOR requests with their actual scores"""
    print("=" * 60)
    print("Updating SOR Request Scores")
    print("=" * 60)

    # Get all SOR requests
    requests = dashboard_db.get_all_sor_requests(limit=1000)

    if not requests:
        print("[!] No SOR requests found")
        return

    print(f"\nFound {len(requests)} SOR requests")
    print("\nUpdating scores...")

    updated = 0
    skipped = 0

    for request in requests:
        sor_id = request['id']
        learner_name = request['learner_name']
        current_score = request.get('overall_score')

        # Fetch learner data from database
        learner_data = db.fetch_all_learner_data(learner_name)

        if not learner_data:
            print(f"[X] ID {sor_id}: Could not find learner data for '{learner_name}'")
            skipped += 1
            continue

        # Calculate the overall score from quiz results
        overall_score = calculate_overall_score(learner_data)

        if current_score == overall_score:
            print(f"[SKIP] ID {sor_id}: {learner_name} - Score already correct ({overall_score:.2f}%)")
            skipped += 1
        else:
            # Update the score
            success = dashboard_db.update_sor_request(sor_id, {
                'overall_score': overall_score
            })

            if success:
                print(f"[OK] ID {sor_id}: {learner_name} - Updated score to {overall_score:.2f}%")
                updated += 1
            else:
                print(f"[X] ID {sor_id}: {learner_name} - Failed to update")
                skipped += 1

    print("\n" + "=" * 60)
    print(f"Update Complete!")
    print(f"   Updated: {updated}")
    print(f"   Skipped: {skipped}")
    print(f"   Total: {len(requests)}")
    print("=" * 60)
    print("\nYou can now refresh the dashboard to see the updated scores.")

if __name__ == "__main__":
    try:
        update_all_scores()
    except Exception as e:
        print(f"\n[X] Error: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to exit...")
