
import sys
import os
import django

# Setup Django path to allow imports if needed, though BKTService is mostly standalone pure Python
# assuming we are running this from 'backend/'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from chatbot.services.bkt_service import BKTService
except ImportError:
    # Fallback if specific django structure isn't set, try relative
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chatbot', 'services'))
    from chatbot.services.bkt_service import BKTService

def demo_bkt():
    bkt = BKTService()
    
    print("--- Scenario 1: Learning via Chat (Standard BKT) ---")
    # Initial Prob: 0.1 (Don't know it)
    p_mastery = 0.1 
    print(f"Initial Mastery: {p_mastery}")

    # Step 1: Student answers a question WRONG
    p_mastery = bkt.update_node(p_mastery, is_correct=False, source_type="tutor")
    
    # Step 2: Student answers CORRECT
    p_mastery = bkt.update_node(p_mastery, is_correct=True, source_type="tutor")

    # Step 3: Student answers CORRECT again
    p_mastery = bkt.update_node(p_mastery, is_correct=True, source_type="tutor")
    print("\n")

    print("--- Scenario 2: Debugging (Strong Concept Signal) ---")
    # Debugging is harder, so success implies high mastery gain (lower slip, high transit)
    p_loop_mastery = 0.3
    print(f"Initial Loop Mastery: {p_loop_mastery}")

    # Student fixes a bug!
    p_loop_mastery = bkt.update_node(p_loop_mastery, is_correct=True, source_type="debug")
    print("\n")

    print("--- Scenario 3: Coding (Medium Signal) ---")
    # Writing code has low guess probability
    p_func_mastery = 0.4
    print(f"Initial Function Mastery: {p_func_mastery}")

    # Student writes correct code
    p_func_mastery = bkt.update_node(p_func_mastery, is_correct=True, source_type="code")

if __name__ == "__main__":
    demo_bkt()
