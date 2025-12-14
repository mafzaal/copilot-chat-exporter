#!/usr/bin/env python3
"""
Test script for Copilot Chat Exporter

This script tests the basic functionality of the chat exporter.
"""

import sys
from pathlib import Path
from datetime import datetime

from copilot_chat_exporter.core.exporter import CopilotChatExporter
from copilot_chat_exporter.core.models import ChatMessage, ChatSession
from copilot_chat_exporter.utils.workspace_finder import VSCodeWorkspaceFinder


def test_basic_functionality():
    """Test basic functionality"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test exporter initialization
        exporter = CopilotChatExporter()
        print("✅ Exporter initialized successfully")
        
        # Test data structures
        test_message = ChatMessage(
            id="test_msg_1",
            timestamp=datetime.now(),
            role="user",
            content="This is a test message"
        )
        print("✅ ChatMessage created successfully")
        
        test_session = ChatSession(
            session_id="test_session_1",
            title="Test Session",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            messages=[test_message]
        )
        print("✅ ChatSession created successfully")
        
        # Test export functions (with dummy data)
        test_export_dir = Path("test_exports")
        test_export_dir.mkdir(exist_ok=True)
        
        # Test JSON export
        json_file = test_export_dir / "test_export.json"
        exporter.export_to_json([test_session], str(json_file))
        if json_file.exists():
            print("✅ JSON export test successful")
            json_file.unlink()  # Clean up
        
        # Test CSV export
        csv_file = test_export_dir / "test_export.csv"
        exporter.export_to_csv([test_session], str(csv_file))
        if csv_file.exists():
            print("✅ CSV export test successful")
            csv_file.unlink()  # Clean up
        
        # Test Markdown export
        md_file = test_export_dir / "test_export.md"
        exporter.export_to_markdown([test_session], str(md_file))
        if md_file.exists():
            print("✅ Markdown export test successful")
            md_file.unlink()  # Clean up
        
        # Clean up test directory
        test_export_dir.rmdir()
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True


def test_workspace_functionality():
    """Test workspace ID detection functionality"""
    print("\n🔍 Testing workspace functionality...")
    
    try:
        # Test workspace finder
        finder = VSCodeWorkspaceFinder()
        print("✅ VSCodeWorkspaceFinder initialized successfully")
        
        # Test finding workspace ID for current directory
        current_dir = str(Path.cwd())
        workspace_id = finder.find_workspace_id(current_dir)
        
        if workspace_id:
            print(f"✅ Found workspace ID for current directory: {workspace_id}")
        else:
            print("ℹ️  No workspace ID found for current directory (this is normal if this folder hasn't been opened in VS Code)")
        
        # Test listing all workspaces
        workspaces = finder.list_all_workspaces()
        print(f"✅ Found {len(workspaces)} total workspaces")
        
        # Test exporter with workspace path
        exporter = CopilotChatExporter(workspace_path=current_dir)
        print("✅ CopilotChatExporter with workspace path initialized successfully")
        
        if exporter.workspace_id:
            print(f"✅ Exporter found workspace ID: {exporter.workspace_id}")
        else:
            print("ℹ️  Exporter didn't find workspace ID (this is normal if this folder hasn't been opened in VS Code)")
        
        return True
        
    except Exception as e:
        print(f"❌ Workspace functionality test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting Copilot Chat Exporter Tests")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        sys.exit(1)
    else:
        print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check dependencies
    try:
        import pydantic
        print(f"✅ Pydantic version: {pydantic.__version__}")
    except ImportError:
        print("❌ Pydantic not found - run 'pip install pydantic'")
        sys.exit(1)
    
    # Run tests
    tests_passed = 0
    total_tests = 2
    
    if test_basic_functionality():
        tests_passed += 1
    
    if test_workspace_functionality():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The exporter is ready to use.")
        print("\nTo export your chat history, run:")
        print("  python -m copilot_chat_exporter.cli.quick_export")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
