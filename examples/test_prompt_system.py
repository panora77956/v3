#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test suite for PR #71: Custom Prompts and JSON Parsing Fixes

Tests:
1. JSON Parsing with Strategy 1b (4 tests)
2. Code Generation for Custom Prompts (2 tests)
3. Round-trip Execution (2 tests)

Total: 8 tests
"""

import json
import os
import sys
import tempfile
from typing import Dict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_story_service import parse_llm_response_safe, _escape_unescaped_strings
from services.prompt_updater import generate_custom_prompts_code, generate_prompts_code


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add(self, name: str, passed: bool, message: str = ""):
        self.tests.append((name, passed, message))
        if passed:
            self.passed += 1
            print(f"✅ {name}")
        else:
            self.failed += 1
            print(f"❌ {name}: {message}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"Test Results: {self.passed}/{total} passed")
        print(f"{'='*60}")
        if self.failed == 0:
            print("🎉 All tests passed!")
        else:
            print(f"⚠️  {self.failed} test(s) failed")
            for name, passed, message in self.tests:
                if not passed:
                    print(f"  - {name}: {message}")
        return self.failed == 0


def test_json_parsing():
    """Test Suite 1: JSON Parsing with Strategy 1b (4 tests)"""
    print("\n" + "="*60)
    print("TEST SUITE 1: JSON Parsing with Strategy 1b")
    print("="*60)
    
    results = TestResults()
    
    # Test 1.1: Parse JSON with literal newlines (the main bug from PR)
    print("\nTest 1.1: Parse JSON with literal newlines")
    json_with_newlines = '''{
    "title": "Test with
literal newline",
    "description": "This has a
newline in the middle"
}'''
    try:
        result = parse_llm_response_safe(json_with_newlines, "Test")
        assert isinstance(result, dict)
        assert "title" in result
        results.add("1.1 JSON with literal newlines", True)
    except Exception as e:
        results.add("1.1 JSON with literal newlines", False, str(e))
    
    # Test 1.2: Parse JSON with tabs
    print("\nTest 1.2: Parse JSON with literal tabs")
    json_with_tabs = '''{
    "title": "Test with\ttabs",
    "items": ["item\t1", "item\t2"]
}'''
    try:
        result = parse_llm_response_safe(json_with_tabs, "Test")
        assert isinstance(result, dict)
        assert "title" in result
        results.add("1.2 JSON with literal tabs", True)
    except Exception as e:
        results.add("1.2 JSON with literal tabs", False, str(e))
    
    # Test 1.3: Parse JSON with carriage returns
    print("\nTest 1.3: Parse JSON with carriage returns")
    json_with_cr = '{"title": "Test with\rcarriage return"}'
    try:
        result = parse_llm_response_safe(json_with_cr, "Test")
        assert isinstance(result, dict)
        assert "title" in result
        results.add("1.3 JSON with carriage returns", True)
    except Exception as e:
        results.add("1.3 JSON with carriage returns", False, str(e))
    
    # Test 1.4: Parse complex JSON (simulating the actual error from char 19335)
    print("\nTest 1.4: Parse complex JSON with multiple issues")
    complex_json = '''{
    "scenes": [
        {
            "description": "A scene with
multiple lines
and\ttabs"
        },
        {
            "voiceover": "Text with\rcarriage\rreturns"
        }
    ]
}'''
    try:
        result = parse_llm_response_safe(complex_json, "Test")
        assert isinstance(result, dict)
        assert "scenes" in result
        assert len(result["scenes"]) == 2
        results.add("1.4 Complex JSON with multiple issues", True)
    except Exception as e:
        results.add("1.4 Complex JSON with multiple issues", False, str(e))
    
    return results


def test_code_generation():
    """Test Suite 2: Code Generation for Custom Prompts (2 tests)"""
    print("\n" + "="*60)
    print("TEST SUITE 2: Code Generation for Custom Prompts")
    print("="*60)
    
    results = TestResults()
    
    # Test 2.1: Generate custom prompts code
    print("\nTest 2.1: Generate custom prompts code")
    custom_prompts = {
        "KHOA HỌC GIÁO DỤC": {
            "PANORA - Nhà Tường thuật": """Bạn là Nhà Tường thuật.

I. QUY TẮC:
CẤM TẠO NHÂN VẬT

II. CẤU TRÚC:
Mở đầu hook"""
        },
        "TEST DOMAIN": {
            "Test Topic": "Simple prompt for testing"
        }
    }
    
    try:
        code = generate_custom_prompts_code(custom_prompts)
        
        # Verify code structure
        assert '# -*- coding: utf-8 -*-' in code
        assert 'CUSTOM_PROMPTS = {' in code
        assert 'def get_custom_prompt(domain: str, topic: str)' in code
        assert '("KHOA HỌC GIÁO DỤC", "PANORA - Nhà Tường thuật")' in code
        assert '("TEST DOMAIN", "Test Topic")' in code
        
        # Verify it's valid Python
        exec(code)
        
        results.add("2.1 Generate custom prompts code", True)
    except Exception as e:
        results.add("2.1 Generate custom prompts code", False, str(e))
    
    # Test 2.2: Generate regular prompts code
    print("\nTest 2.2: Generate regular prompts code")
    regular_prompts = {
        "GIÁO DỤC/HACKS": {
            "Mẹo Vặt": "Bạn là chuyên gia về mẹo vặt",
            "Life Hacks": "You are a life hacks expert"
        }
    }
    
    try:
        code = generate_prompts_code(regular_prompts)
        
        # Verify code structure
        assert '# -*- coding: utf-8 -*-' in code
        assert 'DOMAIN_PROMPTS = {' in code
        assert 'def get_system_prompt(domain, topic)' in code
        assert '"GIÁO DỤC/HACKS"' in code
        
        # Verify it's valid Python
        exec(code)
        
        results.add("2.2 Generate regular prompts code", True)
    except Exception as e:
        results.add("2.2 Generate regular prompts code", False, str(e))
    
    return results


def test_round_trip():
    """Test Suite 3: Round-trip Execution (2 tests)"""
    print("\n" + "="*60)
    print("TEST SUITE 3: Round-trip Execution")
    print("="*60)
    
    results = TestResults()
    
    # Test 3.1: Generate and execute custom prompts code
    print("\nTest 3.1: Generate and execute custom prompts code")
    custom_prompts = {
        "TEST_DOMAIN": {
            "Test Topic": """Multi-line
prompt with
special characters"""
        }
    }
    
    try:
        # Generate code
        code = generate_custom_prompts_code(custom_prompts)
        
        # Execute code in a namespace
        namespace = {}
        exec(code, namespace)
        
        # Verify the function works
        get_custom_prompt = namespace['get_custom_prompt']
        result = get_custom_prompt("TEST_DOMAIN", "Test Topic")
        
        assert result is not None
        assert "Multi-line" in result
        assert "prompt with" in result
        
        # Verify None for non-existent prompt
        none_result = get_custom_prompt("NON_EXISTENT", "Topic")
        assert none_result is None
        
        results.add("3.1 Generate and execute custom prompts code", True)
    except Exception as e:
        results.add("3.1 Generate and execute custom prompts code", False, str(e))
    
    # Test 3.2: Generate and execute regular prompts code
    print("\nTest 3.2: Generate and execute regular prompts code")
    regular_prompts = {
        "DOMAIN_A": {
            "Topic 1": "Prompt for topic 1",
            "Topic 2": "Prompt for topic 2"
        }
    }
    
    try:
        # Generate code
        code = generate_prompts_code(regular_prompts)
        
        # Execute code in a namespace
        namespace = {}
        exec(code, namespace)
        
        # Verify the function works
        get_system_prompt = namespace['get_system_prompt']
        
        # Test with specific topic
        result = get_system_prompt("DOMAIN_A", "Topic 1")
        assert result == "Prompt for topic 1"
        
        # Test with different topic
        result2 = get_system_prompt("DOMAIN_A", "Topic 2")
        assert result2 == "Prompt for topic 2"
        
        # Test empty string for non-existent topic
        result3 = get_system_prompt("DOMAIN_A", "Non-existent Topic")
        assert result3 == ""  # Should return empty string per the implementation
        
        # Test empty string for non-existent domain
        result4 = get_system_prompt("NON_EXISTENT_DOMAIN", "Any Topic")
        assert result4 == ""  # Should return empty string per the implementation
        
        results.add("3.2 Generate and execute regular prompts code", True)
    except Exception as e:
        results.add("3.2 Generate and execute regular prompts code", False, str(e))
    
    return results


def main():
    """Run all test suites"""
    print("\n" + "="*60)
    print("PR #71 TEST SUITE")
    print("Testing: JSON Parsing Fixes & Custom Prompts System")
    print("="*60)
    
    all_results = TestResults()
    
    # Run test suites
    suite1 = test_json_parsing()
    suite2 = test_code_generation()
    suite3 = test_round_trip()
    
    # Combine results
    all_results.passed = suite1.passed + suite2.passed + suite3.passed
    all_results.failed = suite1.failed + suite2.failed + suite3.failed
    all_results.tests = suite1.tests + suite2.tests + suite3.tests
    
    # Print summary
    success = all_results.summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
