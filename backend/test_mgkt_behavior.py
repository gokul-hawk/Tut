import os
import sys
import json
import numpy as np

# Add path for backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import MGKT
try:
    from simulate_advanced_mgkt import ContextAwareMGKT
except ImportError:
    # Use fallback if needed - but it should work
    pass

def test_eureka_detection():
    """
    ASSERTION: For a student who has struggled (10 failures), 
    MGKT MUST detect mastery > 0.8 within 2 successful 'code' interactions.
    """
    print("Running Test: Eureka Detection...")
    model = ContextAwareMGKT("EurekaTest")
    
    # 1. Simulate Struggle (10 Tutor Failures)
    for _ in range(10):
        model.update_with_context(False, "tutor", {})
    
    initial_mastery = model.mastery
    print(f"  - Mastery after 10 failures: {initial_mastery:.4f}")
    
    # 2. Simulate "Aha!" moment (2 High-Score Code Successes)
    # Step 1
    model.update_with_context(True, "code", {"score": 95})
    # Step 2
    model.update_with_context(True, "code", {"score": 98})
    
    final_mastery = model.mastery
    print(f"  - Mastery after 2 successes: {final_mastery:.4f}")
    
    assert final_mastery > 0.8, f"FAILED: Mastery {final_mastery} <= 0.8 after recovery"
    print("  - PASS: Recovery detected rapidly.")
    return True

def test_guess_immunity():
    """
    ASSERTION: For a student using AI heavily, 
    Mastery MUST remain < 0.3 even after 3 consecutive correct answers.
    """
    print("\nRunning Test: Guess Immunity...")
    model = ContextAwareMGKT("GuessImmunityTest")
    
    # 1. Student gets 3 correct answers but with AI=15 (Heavy usage)
    for i in range(3):
        model.update_with_context(True, "code", {"ai_usage": 15})
        print(f"  - Step {i+1} Mastery (AI usage=15): {model.mastery:.4f}")
        
    final_mastery = model.mastery
    assert final_mastery < 0.3, f"FAILED: Mastery {final_mastery} >= 0.3 despite heavy AI usage"
    print("  - PASS: Model correctly skeptical of guessers.")
    return True

def test_expert_stability():
    """
    ASSERTION: For an expert, a single slip MUST NOT drop mastery below 0.7.
    """
    print("\nRunning Test: Expert Stability...")
    model = ContextAwareMGKT("ExpertStabilityTest")
    
    # 1. Establish Mastery (5 successes)
    for _ in range(5):
        model.update_with_context(True, "tutor", {})
    
    master_level = model.mastery
    print(f"  - Mastery after 5 successes: {master_level:.4f}")
    
    # 2. Simulate a single "Slip"
    model.update_with_context(False, "code", {"score": 0})
    post_slip_mastery = model.mastery
    print(f"  - Mastery after 1 slip: {post_slip_mastery:.4f}")
    
    assert post_slip_mastery > 0.7, f"FAILED: Mastery {post_slip_mastery} <= 0.7 after minor slip"
    print("  - PASS: Model stable against minor performance noise.")
    return True

def run_all_behavior_tests():
    print(f"\n{'='*80}")
    print(f"{'MGKT FORMAL BEHAVIOURAL TEST SUITE' :^80}")
    print(f"{'='*80}\n")
    
    results = []
    try:
        results.append(("Eureka Detection", test_eureka_detection()))
    except Exception as e:
        print(f"  - ERROR: {e}")
        results.append(("Eureka Detection", False))
        
    try:
        results.append(("Guess Immunity", test_guess_immunity()))
    except Exception as e:
        print(f"  - ERROR: {e}")
        results.append(("Guess Immunity", False))
        
    try:
        results.append(("Expert Stability", test_expert_stability()))
    except Exception as e:
        print(f"  - ERROR: {e}")
        results.append(("Expert Stability", False))

    print(f"\n{'='*80}")
    print(f"{'FINAL TEST REPORT' :^80}")
    print(f"{'='*80}")
    
    overall_pass = True
    for name, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{name:<30}: {status}")
        if not success: overall_pass = False
        
    print(f"{'='*80}")
    if overall_pass:
        print(f"{'OVERALL SYSTEM STATUS: HEALTHY' :^80}")
    else:
        print(f"{'OVERALL SYSTEM STATUS: ACTION REQUIRED' :^80}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    run_all_behavior_tests()
