#!/usr/bin/env python3
"""
Test script to verify the enhanced response system generates unique responses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import generate_dynamic_response, get_contextual_response, analyze_mood_and_context

def test_response_variety():
    """Test that responses are truly unique and varied"""
    
    print("🧪 Testing Response Variety System")
    print("=" * 50)
    
    # Test different moods and response types
    test_cases = [
        ('stressed', 'funny'),
        ('anxious', 'motivational'),
        ('sad', 'scientific'),
        ('overwhelmed', 'actionable'),
        ('tired', 'funny'),
        ('frustrated', 'motivational')
    ]
    
    responses = []
    
    for mood, response_type in test_cases:
        print(f"\n📝 Testing: {mood} + {response_type}")
        
        # Generate multiple responses for the same input
        for i in range(3):
            response = generate_dynamic_response(response_type, mood, 'general')
            responses.append(response)
            print(f"  Response {i+1}: {response}")
            
            # Check for uniqueness
            if response in responses[:-1]:
                print(f"  ⚠️  WARNING: Duplicate response detected!")
            else:
                print(f"  ✅ Unique response generated")
    
    # Test AI integration (if available)
    print(f"\n🤖 Testing AI Integration")
    print("-" * 30)
    
    try:
        for mood, response_type in test_cases[:2]:  # Test first 2 cases
            print(f"\n📝 AI Test: {mood} + {response_type}")
            response = get_contextual_response(mood, 'general', response_type)
            print(f"  AI Response: {response}")
    except Exception as e:
        print(f"  ⚠️  AI not available: {e}")
    
    # Summary
    print(f"\n📊 Summary")
    print("=" * 30)
    print(f"Total responses generated: {len(responses)}")
    print(f"Unique responses: {len(set(responses))}")
    print(f"Variety score: {len(set(responses))/len(responses)*100:.1f}%")
    
    if len(set(responses)) == len(responses):
        print("🎉 SUCCESS: All responses are unique!")
    else:
        print("⚠️  WARNING: Some duplicate responses detected")
    
    return len(set(responses)) == len(responses)

def test_mood_analysis():
    """Test mood and context analysis"""
    
    print(f"\n🧠 Testing Mood Analysis")
    print("=" * 30)
    
    test_inputs = [
        "I'm so stressed about work",
        "I feel anxious about my relationship",
        "I'm sad and lonely",
        "I'm overwhelmed with everything",
        "I'm tired and exhausted",
        "I'm frustrated with my health"
    ]
    
    for user_input in test_inputs:
        mood, context = analyze_mood_and_context(user_input)
        print(f"Input: '{user_input}'")
        print(f"  Detected mood: {mood}")
        print(f"  Detected context: {context}")
        print()

if __name__ == "__main__":
    print("🚀 Motivo Response System Test")
    print("=" * 50)
    
    # Test mood analysis
    test_mood_analysis()
    
    # Test response variety
    success = test_response_variety()
    
    if success:
        print("\n🎉 All tests passed! The response system is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the response variety.")
    
    print("\n✨ Test completed!") 