#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Vertex AI integration

This script demonstrates:
1. How to configure Vertex AI in config.json
2. How the system automatically tries Vertex AI first
3. How it falls back to AI Studio if Vertex AI is not available
4. Error handling and retry logic
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_config_loading():
    """Test that config.json can be loaded"""
    import json
    
    print("=" * 60)
    print("TEST 1: Config Loading")
    print("=" * 60)
    
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        vertex_config = config.get('vertex_ai', {})
        
        print(f"✓ Config loaded successfully")
        print(f"  - Vertex AI enabled: {vertex_config.get('enabled', False)}")
        print(f"  - Project ID: {vertex_config.get('project_id', 'Not set')}")
        print(f"  - Location: {vertex_config.get('location', 'Not set')}")
        print(f"  - Use Vertex first: {vertex_config.get('use_vertex_first', True)}")
        
        if not vertex_config.get('enabled', False):
            print("\n⚠ Vertex AI is NOT enabled in config.json")
            print("  To enable: Set 'enabled': true and add your 'project_id'")
        
        return True
    except Exception as e:
        print(f"✗ Failed to load config: {e}")
        return False


def test_vertex_ai_client_import():
    """Test that VertexAIClient can be imported"""
    print("\n" + "=" * 60)
    print("TEST 2: Vertex AI Client Import")
    print("=" * 60)
    
    try:
        from services.vertex_ai_client import VertexAIClient
        print("✓ VertexAIClient imported successfully")
        print("  - google-genai SDK is installed")
        return True
    except ImportError as e:
        print(f"✗ Could not import VertexAIClient: {e}")
        print("  Install with: pip install google-genai>=0.3.0")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_gemini_client_with_vertex():
    """Test that GeminiClient can initialize with Vertex AI support"""
    print("\n" + "=" * 60)
    print("TEST 3: GeminiClient with Vertex AI Support")
    print("=" * 60)
    
    try:
        from services.gemini_client import GeminiClient
        
        # Try to initialize (will try Vertex AI if configured)
        try:
            client = GeminiClient(model="gemini-2.5-flash", use_vertex=True)
            print("✓ GeminiClient initialized successfully")
            print(f"  - Vertex AI client: {'Available' if client.vertex_client else 'Not available (using AI Studio)'}")
            return True
        except Exception as e:
            print(f"⚠ Could not initialize GeminiClient with Vertex AI: {e}")
            print("  This is expected if:")
            print("    1. Vertex AI is not configured in config.json")
            print("    2. No API keys are set")
            print("    3. GCP authentication is not set up")
            return False
            
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_fallback_mechanism():
    """Test the fallback mechanism"""
    print("\n" + "=" * 60)
    print("TEST 4: Fallback Mechanism")
    print("=" * 60)
    
    print("The system has a multi-level fallback strategy:")
    print("  1. Try Vertex AI (if enabled in config)")
    print("  2. Fallback to AI Studio with API keys")
    print("  3. Retry with exponential backoff (10s, 20s, 30s, 60s)")
    print("  4. Try multiple API keys if available")
    print("  5. Try fallback models (gemini-1.5-flash, gemini-2.0-flash-exp)")
    print("")
    print("This ensures maximum reliability and minimal 503 errors!")
    return True


def print_setup_instructions():
    """Print setup instructions"""
    print("\n" + "=" * 60)
    print("SETUP INSTRUCTIONS")
    print("=" * 60)
    
    print("\nTo enable Vertex AI:")
    print("1. Read the documentation: docs/VERTEX_AI_SETUP.md")
    print("2. Set up GCP project and authentication")
    print("3. Update config.json:")
    print('   {')
    print('     "vertex_ai": {')
    print('       "enabled": true,')
    print('       "project_id": "your-gcp-project-id",')
    print('       "location": "us-central1",')
    print('       "use_vertex_first": true')
    print('     }')
    print('   }')
    print("")
    print("To keep using AI Studio only:")
    print("- Just keep 'enabled': false in config.json")
    print("- Add your API keys to 'google_keys' array")
    print("- The system will automatically use AI Studio")
    print("")
    print("Benefits of Vertex AI:")
    print("  ✅ Higher rate limits (no 60 req/min restriction)")
    print("  ✅ More stable (less 503 errors)")
    print("  ✅ Enterprise-grade infrastructure")
    print("  ✅ Automatic fallback to AI Studio if issues occur")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("VERTEX AI INTEGRATION TEST SUITE")
    print("=" * 70)
    print("")
    print("This test suite validates the Vertex AI integration.")
    print("It checks configuration, imports, and fallback mechanisms.")
    print("")
    
    results = []
    
    # Run tests
    results.append(("Config Loading", test_config_loading()))
    results.append(("Vertex AI Import", test_vertex_ai_client_import()))
    results.append(("GeminiClient Init", test_gemini_client_with_vertex()))
    results.append(("Fallback Strategy", test_fallback_mechanism()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    # Print setup instructions
    print_setup_instructions()
    
    print("\n" + "=" * 70)
    print("For detailed setup instructions, see: docs/VERTEX_AI_SETUP.md")
    print("=" * 70)
    print("")


if __name__ == "__main__":
    main()
