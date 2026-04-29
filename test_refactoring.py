#!/usr/bin/env python3
"""
Test script to verify the refactored BaseLLMProvider works correctly.
Tests the new intent-based architecture without needing live LLM connections.
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all refactored modules import correctly"""
    print("✓ Testing imports...")
    try:
        from app.models.base import BaseLLMProvider
        print("  ✓ BaseLLMProvider imported successfully")
        return True
    except Exception as e:
        print(f"  ✗ Failed to import: {e}")
        return False

def test_method_exists():
    """Test that new methods exist"""
    print("\n✓ Testing new methods exist...")
    from app.models.base import BaseLLMProvider
    
    methods_to_check = [
        '_detect_intent',
        '_format_response',
        '_ensure_code_blocks',
        '_clean_code_blocks',
        '_get_code_system_prompt',
        '_get_explanation_system_prompt',
        '_get_analysis_system_prompt',
        '_get_howto_system_prompt',
        '_get_default_system_prompt',
    ]
    
    all_exist = True
    for method_name in methods_to_check:
        if hasattr(BaseLLMProvider, method_name):
            print(f"  ✓ {method_name} exists")
        else:
            print(f"  ✗ {method_name} NOT FOUND")
            all_exist = False
    
    return all_exist

def test_old_methods_removed():
    """Test that old rigid methods have been removed"""
    print("\n✓ Testing old methods have been removed...")
    from app.models.base import BaseLLMProvider
    
    old_methods = [
        '_validate_response_structure',
        '_enforce_response_structure',
        # The following might still exist for backward compatibility:
        # '_parse_code_response',
        # '_repair_code_response',
        # '_repair_text_response',
    ]
    
    all_removed = True
    for method_name in old_methods:
        if hasattr(BaseLLMProvider, method_name):
            print(f"  ✗ OLD METHOD STILL EXISTS: {method_name}")
            all_removed = False
        else:
            print(f"  ✓ {method_name} successfully removed")
    
    return all_removed

def test_system_prompts():
    """Test that new system prompts are available"""
    print("\n✓ Testing system prompt methods...")
    from app.models.base import BaseLLMProvider
    
    # Create a minimal instance for testing (won't have a real LLM)
    class TestProvider(BaseLLMProvider):
        def __init__(self):
            self.model_name = "test"
            self.llm = None
            self.memory = None
        
        def initialize(self):
            pass
        
        def setup_chain(self):
            pass
        
        def invoke(self, question: str) -> str:
            return "test"
    
    provider = TestProvider()
    
    prompts_to_check = [
        ('_get_code_system_prompt', []),
        ('_get_explanation_system_prompt', []),
        ('_get_analysis_system_prompt', []),
        ('_get_howto_system_prompt', []),
        ('_get_default_system_prompt', []),
    ]
    
    all_working = True
    for method_name, args in prompts_to_check:
        try:
            method = getattr(provider, method_name)
            prompt = method(*args)
            if prompt and len(prompt) > 20:
                print(f"  ✓ {method_name} returns prompt (~{len(prompt)} chars)")
            else:
                print(f"  ✗ {method_name} returned empty or invalid prompt")
                all_working = False
        except Exception as e:
            print(f"  ✗ {method_name} failed: {e}")
            all_working = False
    
    return all_working

def test_intent_detection_method():
    """Test that intent detection method signature is correct"""
    print("\n✓ Testing intent detection method...")
    from app.models.base import BaseLLMProvider
    import inspect
    
    # Check method signature
    sig = inspect.signature(BaseLLMProvider._detect_intent)
    params = list(sig.parameters.keys())
    
    if 'self' in params and 'question' in params:
        print(f"  ✓ _detect_intent has correct signature: {sig}")
        return True
    else:
        print(f"  ✗ _detect_intent has wrong signature: {sig}")
        return False

def test_format_response_method():
    """Test that _format_response method signature is correct"""
    print("\n✓ Testing format response method...")
    from app.models.base import BaseLLMProvider
    import inspect
    
    sig = inspect.signature(BaseLLMProvider._format_response)
    params = list(sig.parameters.keys())
    
    if 'self' in params and 'text' in params and 'intent' in params:
        print(f"  ✓ _format_response has correct signature: {sig}")
        return True
    else:
        print(f"  ✗ _format_response has wrong signature: {sig}")
        return False

def main():
    print("=" * 60)
    print("BACKEND REFACTORING TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("New methods exist", test_method_exists),
        ("Old methods removed", test_old_methods_removed),
        ("System prompts", test_system_prompts),
        ("Intent detection method", test_intent_detection_method),
        ("Format response method", test_format_response_method),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    print("=" * 60)
    
    return passed_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
