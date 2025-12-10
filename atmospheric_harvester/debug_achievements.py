
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from game.achievements import AchievementManager

def debug_achievements():
    print("Initializing AchievementManager...")
    try:
        manager = AchievementManager()
        print("AchievementManager initialized.")
        
        for uid, achievement in manager.achievements.items():
            print(f"Checking {uid}...")
            if callable(achievement.target):
                print(f"ERROR: Achievement {uid} has a callable target: {achievement.target}")
            elif not isinstance(achievement.target, (int, float)):
                print(f"ERROR: Achievement {uid} has invalid target type: {type(achievement.target)}")
            else:
                # print(f"OK: {uid} target={achievement.target}")
                pass
                
    except Exception as e:
        print(f"Exception during initialization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_achievements()
