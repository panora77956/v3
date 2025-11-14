#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example: How to use Custom Prompts from Google Sheets

This demonstrates the solution to the problem statement:
"Với các custom prompt giờ tôi cập nhật lại các system prompt đó như nào? 
Có cập nhật chung vào với file google sheet đang làm được không?"

Answer: YES! You can now update custom prompts through Google Sheets!
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def example_1_update_from_sheets():
    """
    Example 1: Update prompts from Google Sheets
    
    This demonstrates how to update both regular and custom prompts
    from a single Google Sheets document.
    """
    print("=" * 60)
    print("EXAMPLE 1: Update Prompts from Google Sheets")
    print("=" * 60)
    
    from services.prompt_updater import update_prompts_file
    
    # Path to the prompts file
    services_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'services')
    prompts_file = os.path.join(services_dir, 'domain_prompts.py')
    
    print("\nUpdating prompts from Google Sheets...")
    print("This will update BOTH regular and custom prompts automatically!")
    
    # NOTE: This requires internet connection to Google Sheets
    # In this example, we'll simulate the result
    print("\n[SIMULATED] Connecting to Google Sheets...")
    print("[SIMULATED] Downloading CSV data...")
    print("[SIMULATED] Parsing prompts...")
    print("[SIMULATED] ✅ Success! 5 domains, 15 regular topics, 2 custom prompts")
    
    # In real usage:
    # success, message = update_prompts_file(prompts_file)
    # if success:
    #     print(f"✅ {message}")
    # else:
    #     print(f"❌ {message}")
    
    print("\nFiles that would be updated:")
    print("  - services/domain_prompts.py (regular prompts)")
    print("  - services/domain_custom_prompts.py (custom prompts)")
    

def example_2_check_custom_prompt():
    """
    Example 2: Check if a custom prompt exists for a domain/topic
    
    Shows how the system automatically uses custom prompts when available.
    """
    print("\n\n" + "=" * 60)
    print("EXAMPLE 2: Using Custom Prompts in Code")
    print("=" * 60)
    
    from services.domain_custom_prompts import get_custom_prompt
    
    # Example domain and topic (from problem statement)
    domain = "KHOA HỌC GIÁO DỤC"
    topic = "PANORA - Nhà Tường thuật Khoa học"
    
    print(f"\nChecking for custom prompt...")
    print(f"Domain: {domain}")
    print(f"Topic: {topic}")
    
    custom_prompt = get_custom_prompt(domain, topic)
    
    if custom_prompt:
        print("\n✅ Custom prompt FOUND!")
        print("\nFirst 200 characters:")
        print("-" * 60)
        print(custom_prompt[:200] + "...")
        print("-" * 60)
    else:
        print("\n❌ No custom prompt found - will use regular prompt")


def example_3_google_sheets_format():
    """
    Example 3: Google Sheets format for custom prompts
    
    Shows exactly how to structure the Google Sheets.
    """
    print("\n\n" + "=" * 60)
    print("EXAMPLE 3: Google Sheets Format")
    print("=" * 60)
    
    print("\nYour Google Sheets should have these columns:")
    print("-" * 60)
    print("| Domain              | Topic                    | System Prompt | Type   |")
    print("-" * 60)
    
    print("\nExample rows:")
    print()
    print("Regular prompt example:")
    print("  Domain: GIÁO DỤC/HACKS")
    print("  Topic: Mẹo Vặt (Life Hacks)")
    print("  System Prompt: Bạn là chuyên gia về mẹo vặt...")
    print("  Type: regular  (or leave empty)")
    
    print("\nCustom prompt example (from problem statement):")
    print("  Domain: KHOA HỌC GIÁO DỤC")
    print("  Topic: PANORA - Nhà Tường thuật Khoa học")
    print("  System Prompt: (your multi-line custom prompt)")
    print("  Type: custom  (THIS IS THE KEY!)")
    
    print("\n" + "=" * 60)
    print("IMPORTANT: Set Type='custom' for custom prompts!")
    print("=" * 60)


def example_4_ui_update():
    """
    Example 4: How to update through the UI
    
    Step-by-step instructions for updating in the application.
    """
    print("\n\n" + "=" * 60)
    print("EXAMPLE 4: Update Through UI (Easiest Method)")
    print("=" * 60)
    
    steps = [
        "1. Open the application",
        "2. Go to Settings panel",
        "3. Find the '🔄 Prompts' section",
        "4. (Optional) Update the Google Sheets URL if needed",
        "5. Click '⬇ Update' button",
        "6. Wait for success message",
        "7. Done! Both files are updated automatically"
    ]
    
    print("\nSteps to update prompts in the UI:")
    for step in steps:
        print(f"  {step}")
    
    print("\n✨ Benefits:")
    print("  - Updates BOTH regular and custom prompts")
    print("  - No coding required")
    print("  - Shows progress and results")
    print("  - Error messages if something goes wrong")


def example_5_answer_to_question():
    """
    Example 5: Direct answer to the problem statement question
    
    "Với các custom prompt giờ tôi cập nhật lại các system prompt đó như nào?"
    "Có cập nhật chung vào với file google sheet đang làm được không?"
    """
    print("\n\n" + "=" * 60)
    print("ANSWER TO YOUR QUESTION / TRẢ LỜI CÂU HỎI")
    print("=" * 60)
    
    print("\n🇻🇳 Câu hỏi:")
    print("  'Với các custom prompt giờ tôi cập nhật lại các system prompt đó như nào?")
    print("   Có cập nhật chung vào với file google sheet đang làm được không?'")
    
    print("\n✅ TRẢ LỜI: ĐƯỢC!")
    print("\nCách làm:")
    print("  1. Mở Google Sheets của bạn")
    print("  2. Thêm cột 'Type' nếu chưa có")
    print("  3. Với custom prompts: Set Type = 'custom'")
    print("  4. Với regular prompts: Để trống hoặc ghi 'regular'")
    print("  5. Trong app: Settings → Prompts → Click nút Update")
    print()
    print("Hệ thống sẽ TỰ ĐỘNG:")
    print("  ✓ Cập nhật file domain_prompts.py (regular prompts)")
    print("  ✓ Cập nhật file domain_custom_prompts.py (custom prompts)")
    print("  ✓ Hiển thị kết quả: số domains, topics, custom prompts")
    
    print("\n🇬🇧 Question:")
    print("  'How do I update custom prompts now?")
    print("   Can I update them together in the Google Sheet?'")
    
    print("\n✅ ANSWER: YES!")
    print("\nHow to do it:")
    print("  1. Open your Google Sheets")
    print("  2. Add 'Type' column if not present")
    print("  3. For custom prompts: Set Type = 'custom'")
    print("  4. For regular prompts: Leave empty or set 'regular'")
    print("  5. In app: Settings → Prompts → Click Update button")
    print()
    print("The system will AUTOMATICALLY:")
    print("  ✓ Update domain_prompts.py (regular prompts)")
    print("  ✓ Update domain_custom_prompts.py (custom prompts)")
    print("  ✓ Show results: number of domains, topics, custom prompts")


def example_6_json_error_fix():
    """
    Example 6: The JSON parsing error fix
    
    Addresses the "Unterminated string" error from the problem statement.
    """
    print("\n\n" + "=" * 60)
    print("BONUS: JSON Parsing Error Fix")
    print("=" * 60)
    
    print("\n🐛 Error from problem statement:")
    print("  '[DEBUG] Vertex AI Strategy 1 failed (direct parse):")
    print("   Unterminated string starting at: line 138 column 21 (char 19335)'")
    
    print("\n✅ FIXED!")
    print("\nWhat was the problem?")
    print("  - VertexAI responses sometimes contained literal newlines in JSON strings")
    print("  - Standard JSON parser couldn't handle this")
    
    print("\nHow it's fixed:")
    print("  - Added Strategy 1b: Automatic escape of special characters")
    print("  - When direct parse fails, tries again with escaped strings")
    print("  - Handles newlines (\\n), tabs (\\t), carriage returns (\\r)")
    
    print("\nResult:")
    print("  - JSON responses with special characters now parse successfully")
    print("  - More robust error handling")
    print("  - Better logging of parsing attempts")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("CUSTOM PROMPTS FROM GOOGLE SHEETS - EXAMPLES")
    print("=" * 60)
    
    example_1_update_from_sheets()
    example_2_check_custom_prompt()
    example_3_google_sheets_format()
    example_4_ui_update()
    example_5_answer_to_question()
    example_6_json_error_fix()
    
    print("\n\n" + "=" * 60)
    print("For more details, see: docs/CUSTOM_PROMPTS_GUIDE.md")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
