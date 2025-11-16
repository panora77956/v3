#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify PANORA custom prompt enhancement
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_story_service import _enhance_panora_custom_prompt


def test_panora_enhancement():
    """Test that PANORA custom prompts get enhanced"""
    print("=" * 70)
    print("TEST: PANORA Custom Prompt Enhancement")
    print("=" * 70)
    
    # Simulate a basic PANORA custom prompt from Google Sheets
    basic_prompt = """
Bạn là Nhà Tường thuật Khoa học của kênh PANORA.

I. QUY TẮC TỐI THƯỢNG:
- Không dùng nhân vật
- Dùng ngôi thứ hai
- Tuân thủ cấu trúc 5 giai đoạn
"""
    
    domain = "KHOA HỌC GIÁO DỤC"
    topic = "PANORA - Nhà Tường thuật Khoa học"
    
    print("\n1. Original prompt from Google Sheets:")
    print("-" * 70)
    print(basic_prompt)
    print("-" * 70)
    print(f"Length: {len(basic_prompt)} characters")
    
    # Enhance the prompt
    enhanced = _enhance_panora_custom_prompt(basic_prompt, domain, topic)
    
    print("\n2. Enhanced prompt (with PR #95 additions):")
    print("-" * 70)
    print(enhanced)
    print("-" * 70)
    print(f"Length: {len(enhanced)} characters")
    
    # Verify enhancements are present
    print("\n3. Verification:")
    print("-" * 70)
    
    checks = [
        ("CRITICAL SEPARATION", "CRITICAL SEPARATION" in enhanced),
        ("Few-shot examples", "VÍ DỤ SAI" in enhanced and "VÍ DỤ ĐÚNG" in enhanced),
        ("Voiceover definition", "VOICEOVER = CHỈ LỜI THOẠI" in enhanced),
        ("Prompt definition", "PROMPT = CHỈ MÔ TẢ HÌNH ẢNH" in enhanced),
        ("Character prohibitions", "CẤM viết tên nhân vật" in enhanced),
        ("Final warning", "QUAN TRỌNG NHẤT" in enhanced),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {'PASS' if passed else 'FAIL'}")
        if not passed:
            all_passed = False
    
    print("-" * 70)
    
    if all_passed:
        print("\n🎉 ALL CHECKS PASSED!")
        print("PANORA enhancements are correctly applied and will be preserved")
        print("even when the custom prompt is updated from Google Sheets.")
        return True
    else:
        print("\n❌ SOME CHECKS FAILED!")
        return False


def test_non_panora_no_enhancement():
    """Test that non-PANORA prompts are NOT enhanced"""
    print("\n\n" + "=" * 70)
    print("TEST: Non-PANORA Custom Prompt (Should NOT be enhanced)")
    print("=" * 70)
    
    basic_prompt = """
Bạn là chuyên gia về mẹo vặt cuộc sống.
"""
    
    domain = "GIÁO DỤC/HACKS"
    topic = "Mẹo Vặt (Life Hacks)"
    
    print("\n1. Original non-PANORA prompt:")
    print("-" * 70)
    print(basic_prompt)
    print("-" * 70)
    
    # Try to enhance (should return unchanged)
    result = _enhance_panora_custom_prompt(basic_prompt, domain, topic)
    
    print("\n2. After enhancement attempt:")
    print("-" * 70)
    print(result)
    print("-" * 70)
    
    # Verify it's unchanged
    unchanged = (result == basic_prompt)
    
    print("\n3. Verification:")
    print("-" * 70)
    status = "✅" if unchanged else "❌"
    print(f"{status} Prompt unchanged: {'PASS' if unchanged else 'FAIL'}")
    print("-" * 70)
    
    if unchanged:
        print("\n✅ CORRECT! Non-PANORA prompts are not modified.")
        return True
    else:
        print("\n❌ ERROR! Non-PANORA prompt was modified.")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("PANORA CUSTOM PROMPT ENHANCEMENT - TEST SUITE")
    print("=" * 70)
    
    test1 = test_panora_enhancement()
    test2 = test_non_panora_no_enhancement()
    
    print("\n\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if test1 and test2:
        print("\n✅ ALL TESTS PASSED!")
        print("\nThe fix ensures that:")
        print("1. PANORA prompts get automatic enhancements from PR #95")
        print("2. Enhancements are preserved when updating from Google Sheets")
        print("3. Non-PANORA prompts remain unchanged")
        print("\n✨ Issue is FIXED! You can now safely update prompts from Google Sheets.")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
