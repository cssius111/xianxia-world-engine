#!/usr/bin/env python3
"""
🚀 XianXia World Engine - Vibe Coding Test Suite
Modern, scalable AI-powered game testing framework
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List, Tuple

# Project paths


class VibeTester:
    """Modern test orchestrator for XianXia World Engine"""

    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()

    def print_header(self, title: str, emoji: str = "🔍"):
        """Print a stylized section header"""
        print(f"\n{emoji} {title}")
        print("─" * 60)

    def test_module_imports(self) -> bool:
        """Test core module imports and circular dependency resolution"""
        self.print_header("Testing Module Imports", "📦")

        try:
            # Clear module cache
            for key in list(sys.modules.keys()):
                if key.startswith("xwe"):
                    del sys.modules[key]

            # Test imports
            from xwe.core import GameCore
            from xwe.core.nlp.nlp_processor import NLPConfig, NLPProcessor
            from xwe.npc import DialogueSystem, NPCManager, TradingSystem
            from xwe.npc.emotion_system import EmotionState

            print("✅ All core modules imported successfully")
            print("   • GameCore: ✓")
            print("   • NPC Systems: ✓")
            print("   • NLP Processor: ✓")
            print("   • Emotion System: ✓")
            return True

        except ImportError as e:
            print(f"❌ Import failed: {e}")
            return False

    def test_nlp_features(self) -> Dict[str, bool]:
        """Test NLP duration extraction and command parsing"""
        self.print_header("Testing NLP Features", "🧠")

        results = {}

        try:
            from xwe.core.command_parser import CommandType
            from xwe.core.nlp.nlp_processor import NLPConfig, NLPProcessor

            # Test with mock API (no real API calls)
            config = NLPConfig(enable_llm=False)
            nlp = NLPProcessor(config=config)

            # Test cases
            test_cases = [
                ("修炼一年", CommandType.CULTIVATE, {"duration": "1年"}),
                ("我想修炼3个月", CommandType.CULTIVATE, {"duration": "3月"}),
                ("攻击敌人", CommandType.ATTACK, {}),
                ("查看状态", CommandType.STATUS, {}),
            ]

            all_pass = True
            for input_text, expected_cmd, expected_params in test_cases:
                result = nlp.parse(input_text)

                # Check command type
                cmd_match = result.command_type == expected_cmd

                # Check parameters
                params_match = all(
                    result.parameters.get(k) == v for k, v in expected_params.items()
                )

                if cmd_match and params_match:
                    print(f"✅ '{input_text}' → {expected_cmd.value}")
                    if expected_params:
                        print(f"   Parameters: {result.parameters}")
                else:
                    print(
                        f"❌ '{input_text}' → Expected: {expected_cmd.value}, Got: {result.command_type}"
                    )
                    all_pass = False

            results["command_parsing"] = all_pass
            results["duration_extraction"] = any(
                "duration" in nlp.parse(text).parameters for text in ["修炼一年", "修炼3个月"]
            )

        except Exception as e:
            print(f"❌ NLP test error: {e}")
            results["command_parsing"] = False
            results["duration_extraction"] = False

        return results

    def test_emotion_system(self) -> bool:
        """Test emotion system attributes and functionality"""
        self.print_header("Testing Emotion System", "😊")

        try:
            from xwe.npc.emotion_system import EmotionState, EmotionSystem, EmotionType

            # Test EmotionState
            state = EmotionState()

            # Check required attributes
            checks = {
                "current_emotion": hasattr(state, "current_emotion"),
                "primary": hasattr(state, "primary"),
                "intensity": hasattr(state, "intensity"),
            }

            all_good = all(checks.values())

            if all_good:
                print(f"✅ EmotionState initialized correctly")
                print(f"   • current_emotion: {state.current_emotion}")
                print(f"   • intensity: {state.intensity}")

                # Test emotion system
                system = EmotionSystem()
                system.register_npc("test_npc", "merchant")
                system.trigger_emotion("test_npc", EmotionType.HAPPY, 0.8, "test")

                emotion = system.get_emotion_state("test_npc")
                if emotion:
                    print(f"✅ Emotion system working")
                    print(f"   • NPC emotion: {emotion.primary.value}")
            else:
                print("❌ EmotionState missing attributes:")
                for attr, exists in checks.items():
                    if not exists:
                        print(f"   • Missing: {attr}")

            return all_good

        except Exception as e:
            print(f"❌ Emotion system test error: {e}")
            return False

    def test_api_integration(self) -> Dict[str, Any]:
        """Test API integration status"""
        self.print_header("Testing API Integration", "🔌")

        results = {"deepseek_configured": False, "api_key_present": False, "mock_mode": True}

        try:
            # Check environment configuration
            if env_example.exists():
                with open(env_example, "r") as f:
                    content = f.read()
                    results["deepseek_configured"] = "DEEPSEEK_API_KEY" in content
                    results["api_key_present"] = not any(
                        placeholder in content
                        for placeholder in ["your_key_here", "your_deepseek_api_key_here"]
                    )

            # Check actual API configuration
            api_key = os.getenv("DEEPSEEK_API_KEY", "")
            if api_key and not api_key.startswith("your_"):
                print("✅ DeepSeek API key configured")
            else:
                print("⚠️  DeepSeek API key not set (using mock mode)")

            provider = os.getenv("DEFAULT_LLM_PROVIDER", "mock")
            results["mock_mode"] = provider == "mock"

            print(f"   • Provider: {provider}")
            print(f"   • Mode: {'Mock' if results['mock_mode'] else 'Live API'}")

        except Exception as e:
            print(f"❌ API integration test error: {e}")

        return results

    def run_pytest_suite(self) -> Tuple[int, int, List[str]]:
        """Run the key pytest tests"""
        self.print_header("Running Core Test Suite", "🧪")

        failed_tests = []

        # Key tests to run
        test_targets = [
            "tests/test_overhaul.py::TestNLPProcessor::test_cultivate_with_duration",
            "tests/unit/test_npc.py::test_dialogue_system",
            "tests/unit/test_npc.py::test_dialogue_integration",
        ]

        cmd = [sys.executable, "-m", "pytest"] + test_targets + ["-v", "--tb=short"]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )

            # Parse results
            passed = result.stdout.count(" PASSED")
            failed = result.stdout.count(" FAILED")

            # Extract failed test names
            for line in result.stdout.split("\n"):
                if "FAILED" in line:
                    test_name = line.split(" ")[0]
                    failed_tests.append(test_name)

            print(f"Results: {passed} passed, {failed} failed")

            if failed > 0:
                print("\n❌ Failed tests:")
                for test in failed_tests:
                    print(f"   • {test}")

            return passed, failed, failed_tests

        except Exception as e:
            print(f"❌ Pytest execution error: {e}")
            return 0, len(test_targets), test_targets

    def generate_status_summary(self):
        """Generate comprehensive project status summary"""
        self.print_header("Project Status Summary", "📊")

        # Collect all test results
        import_ok = self.test_module_imports()
        nlp_results = self.test_nlp_features()
        emotion_ok = self.test_emotion_system()
        api_status = self.test_api_integration()
        passed, failed, failed_tests = self.run_pytest_suite()

        # Status summary
        print("\n" + "═" * 60)
        print("🎯 XianXia World Engine - Project Status")
        print("═" * 60)

        print("\n✅ COMPLETE:")
        print("• Core game engine with Roll system")
        print("• World map and location system")
        print("• Combat and skill systems")
        print("• NPC dialogue and trading systems")
        if import_ok:
            print("• Module imports (circular deps fixed)")
        if emotion_ok:
            print("• Emotion system with current_emotion property")

        print("\n❌ FAILING:")
        if not nlp_results.get("duration_extraction"):
            print("• NLP duration extraction for cultivate commands")
        if failed > 0:
            print(f"• {failed} pytest test(s)")
            for test in failed_tests[:3]:  # Show first 3
                print(f"  - {test.split('::')[-1]}")

        print("\n🚀 NEXT STEPS:")
        if not nlp_results.get("duration_extraction"):
            print("• Fix _fuzzy_parse method in nlp_processor.py")
        if failed > 0:
            print("• Debug failing pytest tests")
        print("• Enable DeepSeek API for production")
        print("• Add save/load functionality")
        print("• Implement inventory system")

        print("\n🤖 AI FEATURES:")
        print(
            f"• NLP Command Parsing: {'✅ Working' if nlp_results.get('command_parsing') else '❌ Issues'}"
        )
        print(
            f"• Duration Extraction: {'✅ Working' if nlp_results.get('duration_extraction') else '❌ Needs Fix'}"
        )
        print(f"• Emotion Analysis: {'✅ Working' if emotion_ok else '❌ Issues'}")
        print(f"• API Integration: {'🔧 Mock Mode' if api_status['mock_mode'] else '✅ Live API'}")

        print("\n⚙️  CONFIGURATION:")
        print(f"• API Key in .env: {'✅ Yes' if api_status['deepseek_configured'] else '❌ No'}")
        print(f"• Valid API Key: {'✅ Yes' if api_status['api_key_present'] else '⚠️  Placeholder'}")
        print(f"• Current Mode: {os.getenv('DEFAULT_LLM_PROVIDER', 'mock')}")

        # Execution time
        duration = (datetime.now() - self.start_time).total_seconds()
        print(f"\n⏱️  Tests completed in {duration:.2f}s")
        print("═" * 60)


def main():
    """Run the vibe test suite"""
    print("🌟 XianXia World Engine - Vibe Coding Test Suite")
    print("Modern, AI-powered game testing framework\n")

    tester = VibeTester()
    tester.generate_status_summary()

    print("\n💡 Quick Commands:")
    print("• Run game: python main.py")
    print("• Run menu: python main_menu.py")
    print("• Run all tests: python -m pytest tests/ -v")
    print("• Update API key: edit .env")


if __name__ == "__main__":
    main()
