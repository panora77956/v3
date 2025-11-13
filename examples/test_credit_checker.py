#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Vertex AI Credit Checker
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.vertex_credit_checker import get_credit_checker


def test_credit_checker():
    """Test credit checker functionality"""
    print("=" * 70)
    print("Testing Vertex AI Credit Checker")
    print("=" * 70)
    
    checker = get_credit_checker()
    
    # Test 1: Get billing console URL
    print("\n1. Testing Billing Console URL generation:")
    project_id = "test-project-12345"
    url = checker.get_billing_console_url(project_id)
    print(f"   Project ID: {project_id}")
    print(f"   URL: {url}")
    assert "console.cloud.google.com/billing" in url
    assert project_id in url
    print("   ✅ PASS")
    
    # Test 2: Get Vertex AI console URL
    print("\n2. Testing Vertex AI Console URL generation:")
    location = "us-central1"
    url = checker.get_vertex_ai_console_url(project_id, location)
    print(f"   Project ID: {project_id}")
    print(f"   Location: {location}")
    print(f"   URL: {url}")
    assert "console.cloud.google.com/vertex-ai" in url
    assert project_id in url
    print("   ✅ PASS")
    
    # Test 3: Get quotas console URL
    print("\n3. Testing Quotas Console URL generation:")
    url = checker.get_quotas_console_url(project_id)
    print(f"   Project ID: {project_id}")
    print(f"   URL: {url}")
    assert "console.cloud.google.com/apis" in url
    assert project_id in url
    print("   ✅ PASS")
    
    # Test 4: Get estimated cost info
    print("\n4. Testing Cost Information retrieval:")
    cost_info = checker.get_estimated_cost_info()
    print(f"   Models available: {list(cost_info.keys())}")
    assert "gemini_2_5_flash" in cost_info
    assert "gemini_1_5_pro" in cost_info
    assert "free_tier_info" in cost_info
    print(f"   Gemini 2.5 Flash input price: ${cost_info['gemini_2_5_flash']['input_price_per_1m_chars']}/1M chars")
    print(f"   Gemini 2.5 Flash output price: ${cost_info['gemini_2_5_flash']['output_price_per_1m_chars']}/1M chars")
    print(f"   Free tier: {cost_info['free_tier_info']['amount']} for {cost_info['free_tier_info']['duration']}")
    print("   ✅ PASS")
    
    # Test 5: Format pricing info
    print("\n5. Testing Pricing Info formatting:")
    pricing_text = checker.format_pricing_info()
    print("   Formatted pricing info:")
    print("-" * 70)
    print(pricing_text)
    print("-" * 70)
    assert "Gemini 2.5 Flash" in pricing_text
    assert "$300 credit" in pricing_text
    print("   ✅ PASS")
    
    # Test 6: Get account info text
    print("\n6. Testing Account Info text generation:")
    account_text = checker.get_account_info_text(project_id, location)
    print("   Account info:")
    print("-" * 70)
    print(account_text)
    print("-" * 70)
    assert project_id in account_text
    assert location in account_text
    assert "Billing" in account_text
    assert "Vertex AI" in account_text
    assert "Quotas" in account_text
    print("   ✅ PASS")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
    print("\n💡 Note: Browser opening functions (_open_*_console) are not tested")
    print("   as they require user interaction. They will open URLs in browser.")
    print("\n💡 Integration with UI:")
    print("   - Open Settings Panel")
    print("   - Go to Vertex AI Configuration section")
    print("   - Click '💰 Check' button for any service account")
    print("   - Click '💰 View Pricing Info' button to see pricing details")


if __name__ == "__main__":
    try:
        test_credit_checker()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
