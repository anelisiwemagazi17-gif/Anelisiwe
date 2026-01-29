"""
MindWorx SOR Dashboard Launcher
Run this file to start the dashboard application
"""
import sys
from src.dashboard import main

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("Starting MindWorx SOR Dashboard...")
        print("=" * 60)
        main()
    except KeyboardInterrupt:
        print("\n\nDashboard closed by user")
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
