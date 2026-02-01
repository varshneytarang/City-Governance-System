"""
RUN ALL COMPREHENSIVE TESTS
Executes all architecture verification tests in sequence
"""

import subprocess
import sys
import time
from datetime import datetime

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def run_test(test_name, command):
    """Run a test and return success/failure"""
    print(f"\n▶ Running: {test_name}")
    print(f"  Command: {command}")
    print("-" * 80)
    
    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=False)
    elapsed = time.time() - start_time
    
    if result.returncode == 0:
        print(f"✅ PASSED in {elapsed:.2f}s")
        return True
    else:
        print(f"❌ FAILED (exit code: {result.returncode})")
        return False

def main():
    """Run all tests"""
    print_header("COMPREHENSIVE ARCHITECTURE TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tests = [
        ("Architecture Verification", "python verify_architecture.py"),
        ("Transparency Logging Tests", "python -m pytest test_transparency_logging.py -v"),
        ("Coordination Deadlock Tests", "python -m pytest test_coordination_deadlock.py::TestMultiAgentCoordination -v"),
    ]
    
    results = []
    total_start = time.time()
    
    for test_name, command in tests:
        success = run_test(test_name, command)
        results.append((test_name, success))
        time.sleep(1)  # Brief pause between tests
    
    total_elapsed = time.time() - total_start
    
    # Print Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    print("Test Results:")
    print("-" * 80)
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*80)
    print(f"Total: {passed}/{len(results)} tests passed")
    print(f"Time: {total_elapsed:.2f}s")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - ARCHITECTURE FULLY OPERATIONAL")
        print("="*80)
        return 0
    else:
        print(f"\n⚠️ {failed} TEST(S) FAILED - REVIEW REQUIRED")
        print("="*80)
        return 1

if __name__ == "__main__":
    sys.exit(main())
