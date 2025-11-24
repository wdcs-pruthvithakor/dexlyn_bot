#!/usr/bin/env python3
"""
Comprehensive Test Runner for Dexlyn Perpetuals Trading Bot
Runs all test cases systematically
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict

# Add parent directory to path to import the bot
sys.path.append('..')
from dexlyn_bot import AdvancedDexlynTradingBot

class TestSuiteRunner:
    """Run comprehensive test suites for the trading bot"""
    
    def __init__(self, config_dir: str = "."):
        self.config_dir = Path(config_dir)
        self.test_cases_dir = self.config_dir / "test_cases"
        self.results = {}
        
    def discover_test_cases(self):
        """Discover all test case files"""
        test_cases = {}
        
        categories = [
            "basic_orders",
            "position_flows", 
            "risk_management",
            "multi_wallet",
            "advanced_scenarios",
            "stress_tests",
            "specialized"
        ]
        
        for category in categories:
            category_path = self.test_cases_dir / category
            if category_path.exists():
                for test_file in category_path.glob("*.json"):
                    test_cases[test_file.stem] = str(test_file)
        
        return test_cases
    
    def run_test_suite(self, suite_name: str = "all"):
        """Run specific test suite or all tests"""
        all_tests = self.discover_test_cases()
        
        if suite_name == "all":
            tests_to_run = all_tests
        elif suite_name in all_tests:
            tests_to_run = {suite_name: all_tests[suite_name]}
        else:
            # Try to find by category or partial match
            tests_to_run = {}
            for test_name, test_file in all_tests.items():
                if suite_name in test_name:
                    tests_to_run[test_name] = test_file
        
        if not tests_to_run:
            print(f"❌ No test cases found for: {suite_name}")
            available_tests = list(all_tests.keys())
            print(f"📋 Available tests: {available_tests}")
            return
        
        print(f"🎯 Running {len(tests_to_run)} test cases...")
        
        for test_name, test_file in tests_to_run.items():
            print(f"\n{'='*60}")
            print(f"🧪 TEST FILE: {test_file}")
            
            try:
                # Load test file to display info
                with open(test_file, 'r') as f:
                    test_data = json.load(f)
                
                # Get first strategy name and config
                strategy_name = list(test_data.keys())[0]
                strategy_config = test_data[strategy_name]
                
                print(f"📋 Strategy: {strategy_config.get('name', strategy_name)}")
                print(f"📝 {strategy_config.get('description', '')}")
                print(f"🔧 Orders: {len(strategy_config.get('orders', []))}")
                print(f"{'='*60}")
                
                # Run bot with strategy file
                bot = AdvancedDexlynTradingBot(self.config_dir)
                bot.load_custom_strategies(test_file)
                
                success = bot.executor.execute_strategy(strategy_name)
                
                self.results[test_name] = {
                    "status": "PASS" if success else "FAIL",
                    "strategy": strategy_config.get('name', strategy_name),
                    "orders_executed": len(strategy_config.get('orders', [])),
                    "file": test_file
                }
                
                print(f"✅ {test_name} - {'PASS' if success else 'FAIL'}")
                
            except Exception as e:
                print(f"❌ {test_name} - ERROR: {e}")
                import traceback
                traceback.print_exc()
                self.results[test_name] = {
                    "status": "ERROR", 
                    "error": str(e),
                    "file": test_file
                }
            
            # Wait between tests
            time.sleep(5)
        
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test results summary"""
        print(f"\n{'='*60}")
        print("🎯 TEST SUITE SUMMARY")
        print(f"{'='*60}")
        
        passed = sum(1 for r in self.results.values() if r['status'] == 'PASS')
        failed = sum(1 for r in self.results.values() if r['status'] == 'FAIL') 
        errors = sum(1 for r in self.results.values() if r['status'] == 'ERROR')
        total = len(self.results)
        
        print(f"📊 Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"💥 Errors: {errors}")
        
        if total > 0:
            print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        print(f"\n📋 Detailed Results:")
        for test_name, result in self.results.items():
            status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "💥"
            orders_info = f" ({result.get('orders_executed', 0)} orders)" if result['status'] != 'ERROR' else ""
            print(f"  {status_icon} {test_name}: {result['status']}{orders_info}")

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dexlyn Trading Bot Test Suite Runner")
    parser.add_argument("--suite", default="all", help="Test suite to run (all, basic, risk, etc.)")
    parser.add_argument("--config-dir", default=".", help="Configuration directory")
    parser.add_argument("--list", action="store_true", help="List all available tests")
    
    args = parser.parse_args()
    
    print("🚀 DEXLYN TRADING BOT - COMPREHENSIVE TEST SUITE")
    print("📁 Running tests from: test_cases/")
    
    runner = TestSuiteRunner(args.config_dir)
    
    if args.list:
        tests = runner.discover_test_cases()
        print("📋 AVAILABLE TEST FILES:")
        for test_name, test_file in tests.items():
            print(f"  🧪 {test_name} -> {test_file}")
        return
    
    runner.run_test_suite(args.suite)

if __name__ == "__main__":
    main()