"""
Test Runner with Rate Limit Management

Runs tests in an optimized order to respect API rate limits.
Runs mock-based tests first (no API calls), then integration tests with delays.
"""

import subprocess
import sys
import time


def run_test_suite(name, file_path, markers=None):
    """Run a single test suite with optional markers"""
    print(f"\n{'='*80}")
    print(f"Running: {name}")
    print(f"{'='*80}\n")
    
    cmd = [sys.executable, "-m", "pytest", file_path, "-v", "--tb=short"]
    if markers:
        cmd.extend(["-m", markers])
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    """Run all test suites in optimized order"""
    start_time = time.time()
    results = {}
    
    print("="*80)
    print("CITY GOVERNANCE SYSTEM - TEST SUITE")
    print("Running tests with rate limit optimization")
    print("="*80)
    
    # Phase 1: Mock-based unit tests (no API calls, fast)
    print("\n*** PHASE 1: Unit Tests (Mocked - No API Calls) ***\n")
    results["Unit Tests (Mocked)"] = run_test_suite(
        "Unit Tests with Mocked LLM",
        "tests/test_unit_nodes_mock.py"
    )
    
    # Phase 2: Integration tests with rate limiting
    print("\n*** PHASE 2: Integration Tests (Rate Limited) ***\n")
    print("Note: These tests will take longer due to rate limiting (2.1s delay between requests)")
    results["Integration Tests"] = run_test_suite(
        "Integration Tests (Rate Limited)",
        "tests/test_integration_rate_limited.py"
    )
    
    # Phase 3: Original unit tests (if they exist and use real API)
    # Only run if explicitly requested
    # print("\n*** PHASE 3: Original Unit Tests (Optional) ***\n")
    # results["Unit Tests (Original)"] = run_test_suite(
    #     "Original Unit Tests",
    #     "tests/test_unit_nodes.py"
    # )
    
    # Summary
    elapsed_time = time.time() - start_time
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for suite_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{suite_name:.<50} {status}")
    
    print(f"\nTotal: {passed}/{total} test suites passed")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    print("="*80)
    
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
