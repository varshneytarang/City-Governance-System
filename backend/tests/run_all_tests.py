"""
Test Runner Script

Runs all tests with comprehensive reporting.
"""

import subprocess
import sys
import os
from pathlib import Path

# Ensure we're in the right directory
os.chdir(Path(__file__).parent.parent)


def run_tests():
    """Run all test suites"""
    
    print("=" * 80)
    print("RUNNING COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()
    
    # Test configurations
    test_configs = [
        {
            "name": "Unit Tests",
            "cmd": ["pytest", "tests/test_unit_nodes.py", "-v", "--tb=short"],
            "description": "Testing individual node functionality"
        },
        {
            "name": "Integration Tests",
            "cmd": ["pytest", "tests/test_integration_workflow.py", "-v", "--tb=short", "-x"],
            "description": "Testing complete workflow end-to-end"
        },
        {
            "name": "LLM Robustness Tests",
            "cmd": ["pytest", "tests/test_llm_robustness.py", "-v", "--tb=short"],
            "description": "Testing LLM integration and fallback"
        },
        {
            "name": "Loop Detection Tests",
            "cmd": ["pytest", "tests/test_loop_detection.py", "-v", "--tb=short"],
            "description": "Testing loop prevention and timeouts"
        },
        {
            "name": "All Tests with Coverage",
            "cmd": ["pytest", "tests/", "-v", "--tb=short", "--durations=10"],
            "description": "Running all tests with performance metrics"
        }
    ]
    
    results = []
    
    for config in test_configs:
        print(f"\n{'=' * 80}")
        print(f"🧪 {config['name']}")
        print(f"   {config['description']}")
        print(f"{'=' * 80}\n")
        
        try:
            result = subprocess.run(
                config["cmd"],
                capture_output=False,
                text=True,
                timeout=300  # 5 minute timeout per suite
            )
            
            success = result.returncode == 0
            results.append({
                "name": config["name"],
                "success": success,
                "returncode": result.returncode
            })
            
            if success:
                print(f"\n✅ {config['name']} PASSED\n")
            else:
                print(f"\n❌ {config['name']} FAILED (exit code: {result.returncode})\n")
        
        except subprocess.TimeoutExpired:
            print(f"\n⚠️  {config['name']} TIMEOUT\n")
            results.append({
                "name": config["name"],
                "success": False,
                "returncode": -1
            })
        except Exception as e:
            print(f"\n❌ {config['name']} ERROR: {e}\n")
            results.append({
                "name": config["name"],
                "success": False,
                "returncode": -1
            })
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status}  {result['name']}")
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} test suites passed")
    print("=" * 80)
    
    return all(r["success"] for r in results)


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
