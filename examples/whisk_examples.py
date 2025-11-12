#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisk Service Usage Examples

Demonstrates various use cases for the enhanced Whisk service.
Make sure to configure authentication in config.json before running.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services import whisk_service


def example_1_simple_generation():
    """Example 1: Simple text-to-image generation"""
    print("\n" + "="*60)
    print("Example 1: Simple Text-to-Image Generation")
    print("="*60)
    
    img = whisk_service.generate_image_text_only(
        prompt="A cute cat wearing sunglasses on a beach",
        aspect_ratio="IMAGE_ASPECT_RATIO_SQUARE",
        log_callback=print
    )
    
    if img:
        output_path = "/tmp/whisk_cat.png"
        with open(output_path, "wb") as f:
            f.write(img)
        print(f"\n✓ Image saved to: {output_path}")
        return True
    else:
        print("\n✗ Generation failed")
        return False


def example_2_high_quality():
    """Example 2: High-quality generation with specific model"""
    print("\n" + "="*60)
    print("Example 2: High-Quality Generation with Imagen 4")
    print("="*60)
    
    img = whisk_service.generate_image_text_only(
        prompt="Majestic mountain range during golden hour, photorealistic",
        image_model="IMAGEN_4",  # Best quality model
        aspect_ratio="IMAGE_ASPECT_RATIO_LANDSCAPE",
        seed=12345,  # For reproducibility
        log_callback=print
    )
    
    if img:
        output_path = "/tmp/whisk_mountain.png"
        with open(output_path, "wb") as f:
            f.write(img)
        print(f"\n✓ Image saved to: {output_path}")
        return True
    else:
        print("\n✗ Generation failed")
        return False


def example_3_project_management():
    """Example 3: Project management workflow"""
    print("\n" + "="*60)
    print("Example 3: Project Management Workflow")
    print("="*60)
    
    # Create a new project
    print("\n1. Creating new project...")
    project_id = whisk_service.create_project(
        title="Whisk Examples Collection",
        log_callback=print
    )
    
    if not project_id:
        print("\n✗ Failed to create project")
        return False
    
    print(f"\n✓ Created project: {project_id}")
    
    # Generate an image in the project
    print("\n2. Generating image in project...")
    img = whisk_service.generate_image_text_only(
        prompt="A peaceful garden with colorful flowers",
        project_id=project_id,
        log_callback=print
    )
    
    if img:
        output_path = "/tmp/whisk_garden.png"
        with open(output_path, "wb") as f:
            f.write(img)
        print(f"\n✓ Image saved to: {output_path}")
    
    # Rename the project
    print("\n3. Renaming project...")
    renamed_id = whisk_service.rename_project(
        project_id=project_id,
        new_name="Garden Images Collection",
        log_callback=print
    )
    
    if renamed_id:
        print(f"\n✓ Project renamed: {renamed_id}")
    
    # List projects
    print("\n4. Listing recent projects...")
    projects = whisk_service.get_project_history(
        limit=5,
        log_callback=print
    )
    
    if projects:
        print(f"\n✓ Found {len(projects)} projects:")
        for p in projects[:3]:  # Show first 3
            name = p.get('workflowMetadata', {}).get('workflowName', 'Unnamed')
            wid = p.get('workflowId', 'Unknown')
            print(f"  - {name} ({wid[:20]}...)")
    
    return True


def example_4_batch_generation():
    """Example 4: Batch generation with different seeds"""
    print("\n" + "="*60)
    print("Example 4: Batch Generation with Seeds")
    print("="*60)
    
    base_prompt = "A serene lake at"
    times = ["dawn", "noon", "sunset", "night"]
    
    success_count = 0
    
    for i, time in enumerate(times):
        print(f"\n{i+1}. Generating: {base_prompt} {time}...")
        
        img = whisk_service.generate_image_text_only(
            prompt=f"{base_prompt} {time}, peaceful atmosphere",
            seed=1000 + i,  # Different seed for variety
            aspect_ratio="IMAGE_ASPECT_RATIO_LANDSCAPE",
            log_callback=lambda msg: None  # Silent mode
        )
        
        if img:
            output_path = f"/tmp/whisk_lake_{time}.png"
            with open(output_path, "wb") as f:
                f.write(img)
            print(f"   ✓ Saved to: {output_path}")
            success_count += 1
        else:
            print(f"   ✗ Failed")
    
    print(f"\n✓ Generated {success_count}/{len(times)} images")
    return success_count > 0


def example_5_aspect_ratios():
    """Example 5: Generate same prompt with different aspect ratios"""
    print("\n" + "="*60)
    print("Example 5: Same Prompt, Different Aspect Ratios")
    print("="*60)
    
    prompt = "A modern coffee shop interior, cozy atmosphere"
    
    ratios = [
        ("IMAGE_ASPECT_RATIO_PORTRAIT", "portrait"),
        ("IMAGE_ASPECT_RATIO_LANDSCAPE", "landscape"),
        ("IMAGE_ASPECT_RATIO_SQUARE", "square"),
    ]
    
    success_count = 0
    
    for ratio_const, ratio_name in ratios:
        print(f"\nGenerating with {ratio_name} aspect ratio...")
        
        img = whisk_service.generate_image_text_only(
            prompt=prompt,
            aspect_ratio=ratio_const,
            log_callback=lambda msg: None  # Silent
        )
        
        if img:
            output_path = f"/tmp/whisk_coffee_{ratio_name}.png"
            with open(output_path, "wb") as f:
                f.write(img)
            print(f"✓ Saved to: {output_path}")
            success_count += 1
        else:
            print(f"✗ Failed")
    
    print(f"\n✓ Generated {success_count}/{len(ratios)} variations")
    return success_count > 0


def example_6_model_comparison():
    """Example 6: Compare different Imagen models"""
    print("\n" + "="*60)
    print("Example 6: Model Comparison")
    print("="*60)
    
    prompt = "A futuristic cityscape at night"
    
    models = [
        ("IMAGEN_2", "imagen2"),
        ("IMAGEN_3", "imagen3"),
        ("IMAGEN_3_5", "imagen3_5"),
    ]
    
    print(f"\nPrompt: {prompt}\n")
    
    success_count = 0
    
    for model_name, file_suffix in models:
        print(f"Generating with {model_name}...")
        
        img = whisk_service.generate_image_text_only(
            prompt=prompt,
            image_model=model_name,
            aspect_ratio="IMAGE_ASPECT_RATIO_LANDSCAPE",
            seed=999,  # Same seed for comparison
            log_callback=lambda msg: None
        )
        
        if img:
            output_path = f"/tmp/whisk_city_{file_suffix}.png"
            with open(output_path, "wb") as f:
                f.write(img)
            print(f"✓ {model_name}: {output_path}")
            success_count += 1
        else:
            print(f"✗ {model_name}: Failed")
    
    print(f"\n✓ Generated {success_count}/{len(models)} variations")
    return success_count > 0


def check_authentication():
    """Check if authentication is configured"""
    print("\n" + "="*60)
    print("Checking Authentication")
    print("="*60)
    
    try:
        # Try to get credentials
        session_cookie = whisk_service.get_session_cookies()
        bearer_token = whisk_service.get_bearer_token()
        print("✓ Session cookie configured")
        print("✓ Bearer token configured")
        return True
    except whisk_service.WhiskError as e:
        print("\n✗ Authentication not configured:")
        print(str(e))
        return False


def main():
    """Run examples"""
    print("\n" + "="*80)
    print("Whisk Service Enhanced - Usage Examples")
    print("="*80)
    
    # Check authentication first
    if not check_authentication():
        print("\n" + "="*80)
        print("Please configure authentication before running examples.")
        print("See docs/WHISK_SERVICE_ENHANCED.md for instructions.")
        print("="*80)
        return 1
    
    # List of examples
    examples = [
        ("Simple Generation", example_1_simple_generation),
        ("High-Quality Generation", example_2_high_quality),
        ("Project Management", example_3_project_management),
        ("Batch Generation", example_4_batch_generation),
        ("Aspect Ratios", example_5_aspect_ratios),
        ("Model Comparison", example_6_model_comparison),
    ]
    
    # Run examples
    print("\n" + "="*80)
    print("Running Examples")
    print("="*80)
    
    results = []
    
    for i, (name, func) in enumerate(examples, 1):
        try:
            print(f"\n{'='*80}")
            print(f"Running Example {i}/{len(examples)}: {name}")
            print('='*80)
            
            result = func()
            results.append((name, result))
            
            if result:
                print(f"\n✓ Example {i} completed successfully")
            else:
                print(f"\n✗ Example {i} failed")
                
        except Exception as e:
            print(f"\n✗ Example {i} raised exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*80)
    print("Examples Summary")
    print("="*80)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
    
    success_count = sum(1 for _, s in results if s)
    total = len(results)
    
    print("\n" + "="*80)
    print(f"Completed: {success_count}/{total} examples successful")
    print("="*80)
    
    # Note about output files
    if success_count > 0:
        print("\nGenerated images saved to /tmp/whisk_*.png")
    
    return 0 if success_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
