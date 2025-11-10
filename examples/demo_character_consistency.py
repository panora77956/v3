#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Character Consistency Enhancements
Tests the new costume, accessory, and weapon tracking features
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.google.character_bible import (
    CharacterBible,
    create_character_bible,
    inject_character_consistency,
    inject_style_consistency,
    inject_scene_transition,
    format_character_bible_for_display
)


def test_character_bible_creation():
    """Test creating a character bible with enhanced features"""
    print("=" * 60)
    print("TEST 1: Character Bible Creation with Enhanced Features")
    print("=" * 60)
    
    video_concept = "Epic fantasy adventure"
    script = """
    Scene 1: A warrior in black leather armor, wielding a silver sword, 
    wearing a golden necklace and a red cape, stands in the forest.
    
    Scene 2: The warrior fights an orc using his silver sword.
    """
    
    # Create character bible
    bible = create_character_bible(video_concept, script)
    
    # Display bible
    print("\nGenerated Character Bible:")
    print(format_character_bible_for_display(bible))
    
    # Check that characters were created
    assert len(bible.characters) > 0, "No characters were created"
    
    print("\n✓ Character bible created successfully!")
    print(f"  - Total characters: {len(bible.characters)}")
    
    return bible


def test_character_consistency_injection():
    """Test character consistency injection with new features"""
    print("\n" + "=" * 60)
    print("TEST 2: Character Consistency Injection")
    print("=" * 60)
    
    # Create a simple character bible
    bible = CharacterBible()
    bible.add_character({
        "name": "John Smith",
        "role": "Hero",
        "key_trait": "Brave",
        "visual_identity": "Black leather jacket, blue jeans, brown eyes, short black hair, wearing silver watch, carrying a pistol",
        "physical_blueprint": {
            "age_range": "30-35",
            "race_ethnicity": "Caucasian",
            "height": "tall (180cm)",
            "build": "athletic",
            "skin_tone": "fair"
        },
        "hair_dna": {
            "color": "black",
            "length": "short",
            "style": "neat",
            "texture": "straight"
        },
        "eye_signature": {
            "color": "brown",
            "shape": "almond",
            "expression": "focused"
        },
        "facial_map": {
            "nose": "average",
            "lips": "medium",
            "jawline": "strong",
            "distinguishing_marks": "scar on left cheek"
        },
        "costume": {
            "default_style": "black leather jacket, blue jeans",
            "color_palette": "black, blue",
            "condition": "worn"
        },
        "accessories": ["silver watch"],
        "weapons": ["pistol"],
        "consistency_anchors": [
            "1. Black leather jacket always worn",
            "2. Silver watch on left wrist",
            "3. Scar on left cheek",
            "4. Short black hair",
            "5. Athletic build"
        ]
    })
    
    # Test injection
    scene_prompt = "John is running through the city streets"
    
    # Test with costume and accessories enabled
    enhanced_prompt = inject_character_consistency(
        scene_prompt, 
        bible,
        include_costume=True,
        include_accessories=True
    )
    
    print("\nOriginal prompt:")
    print(f"  {scene_prompt}")
    
    print("\nEnhanced prompt with character consistency:")
    print(enhanced_prompt)
    
    # Verify consistency details are present
    assert "John Smith" in enhanced_prompt
    assert "black leather jacket" in enhanced_prompt.lower() or "jacket" in enhanced_prompt.lower()
    assert "silver watch" in enhanced_prompt.lower() or "watch" in enhanced_prompt.lower()
    assert "pistol" in enhanced_prompt.lower()
    
    print("\n✓ Character consistency injection working correctly!")
    print("  - Costume details: ✓")
    print("  - Accessories: ✓")
    print("  - Weapons: ✓")
    

def test_style_consistency():
    """Test style consistency injection"""
    print("\n" + "=" * 60)
    print("TEST 3: Style Consistency Injection")
    print("=" * 60)
    
    scene_prompt = "A hero walks through a dark alley"
    styles = ["Cinematic", "Anime", "Documentary", "3D"]
    
    for style in styles:
        enhanced = inject_style_consistency(scene_prompt, style)
        print(f"\nStyle: {style}")
        print(f"Enhanced: {enhanced[:100]}...")
        assert f"[STYLE:" in enhanced, f"Style marker not found for {style}"
        assert style.lower() in enhanced.lower() or "maintain" in enhanced.lower()
    
    print("\n✓ Style consistency injection working for all styles!")


def test_scene_transitions():
    """Test scene transition injection"""
    print("\n" + "=" * 60)
    print("TEST 4: Scene Transition Injection")
    print("=" * 60)
    
    prev_prompt = "John stands in a coffee shop, ordering a drink"
    curr_prompt = "John walks outside into the rain"
    
    transitions = ["cut", "fade", "dissolve", "match_cut"]
    
    for transition in transitions:
        enhanced = inject_scene_transition(curr_prompt, prev_prompt, transition)
        print(f"\nTransition: {transition}")
        print(f"Enhanced: {enhanced[:100]}...")
        assert "[SCENE TRANSITION:" in enhanced, f"Transition marker not found for {transition}"
    
    # Test first scene (no previous)
    first_scene = inject_scene_transition(curr_prompt, None, "cut")
    assert first_scene == curr_prompt, "First scene should not have transition"
    
    print("\n✓ Scene transition injection working for all types!")


def test_scene_continuity_validation():
    """Test scene continuity validation"""
    print("\n" + "=" * 60)
    print("TEST 5: Scene Continuity Validation")
    print("=" * 60)
    
    from services.llm_story_service import _validate_scene_continuity
    
    # Test case 1: Good continuity
    good_scenes = [
        {
            "location": "office",
            "time_of_day": "morning",
            "characters": ["John", "Mary"],
            "transition_from_previous": ""
        },
        {
            "location": "office",
            "time_of_day": "morning",
            "characters": ["John", "Mary"],
            "transition_from_previous": "Continuing conversation in same office"
        },
        {
            "location": "coffee shop",
            "time_of_day": "afternoon",
            "characters": ["John"],
            "transition_from_previous": "John leaves office and walks to coffee shop"
        }
    ]
    
    issues = _validate_scene_continuity(good_scenes)
    print(f"\nGood scenes - Issues found: {len(issues)}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    
    # Test case 2: Bad continuity
    bad_scenes = [
        {
            "location": "office",
            "time_of_day": "morning",
            "characters": ["John", "Mary"],
            "transition_from_previous": ""
        },
        {
            "location": "forest",
            "time_of_day": "night",
            "characters": ["Sarah"],
            "transition_from_previous": ""
        }
    ]
    
    issues = _validate_scene_continuity(bad_scenes)
    print(f"\nBad scenes - Issues found: {len(issues)}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    
    assert len(issues) > 0, "Should have found continuity issues in bad scenes"
    
    print("\n✓ Scene continuity validation working correctly!")


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 5 + "CHARACTER CONSISTENCY ENHANCEMENT TESTS" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        # Run tests
        bible = test_character_bible_creation()
        test_character_consistency_injection()
        test_style_consistency()
        test_scene_transitions()
        test_scene_continuity_validation()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe character consistency enhancements are working correctly.")
        print("\nKey improvements:")
        print("  1. ✓ Costume/clothing tracking")
        print("  2. ✓ Accessories tracking")
        print("  3. ✓ Weapons tracking")
        print("  4. ✓ Style consistency enforcement")
        print("  5. ✓ Scene transition support")
        print("  6. ✓ Scene continuity validation")
        print()
        
        return 0
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED!")
        print("=" * 60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
