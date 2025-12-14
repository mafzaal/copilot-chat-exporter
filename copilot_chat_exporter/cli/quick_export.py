#!/usr/bin/env python3
"""
Quick export utility for Copilot Chat history
"""

import sys
from pathlib import Path
from datetime import datetime

from copilot_chat_exporter.core.exporter import CopilotChatExporter


def quick_export(workspace_path=None):
    """Perform a quick export with default settings"""
    print("🤖 Copilot Chat History Exporter")
    print("=" * 40)
    
    workspace_display = workspace_path or "current directory"
    print(f"📁 Workspace: {workspace_display}")
    
    # Create exports directory if it doesn't exist
    exports_dir = Path("exports")
    exports_dir.mkdir(exist_ok=True)
    
    # Initialize exporter
    exporter = CopilotChatExporter(workspace_path=workspace_path)
    
    # Extract chat history
    print("📦 Extracting chat history...")
    sessions = exporter.extract_chat_history()
    
    if not sessions:
        print("❌ No chat history found!")
        print("\nPossible reasons:")
        print("• Copilot chat hasn't been used yet")
        print("• Chat database is in a different location")
        print("• Insufficient permissions to access the database")
        print("• Workspace ID could not be found")
        if exporter.workspace_id:
            print(f"• Found workspace ID: {exporter.workspace_id}")
        else:
            print(f"• No workspace ID found for: {exporter.workspace_path}")
        return
    
    total_messages = sum(len(session.messages) for session in sessions)
    print(f"✅ Found {len(sessions)} sessions with {total_messages} messages")
    if exporter.workspace_id:
        print(f"🔑 Workspace ID: {exporter.workspace_id}")
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    workspace_name = Path(workspace_path or Path.cwd()).name
    
    # Export to multiple formats
    formats = ['json', 'markdown', 'csv']
    
    for fmt in formats:
        filename = exports_dir / f"copilot_chat_{workspace_name}_{timestamp}.{fmt}"
        
        try:
            if fmt == 'json':
                exporter.export_to_json(sessions, str(filename))
            elif fmt == 'markdown':
                exporter.export_to_markdown(sessions, str(filename))
            elif fmt == 'csv':
                exporter.export_to_csv(sessions, str(filename))
            
            print(f"📄 Exported to {filename}")
            
        except Exception as e:
            print(f"❌ Failed to export {fmt}: {e}")
    
    print("\n🎉 Export completed!")
    print(f"📁 Files saved in: {exports_dir.absolute()}")


def show_stats(workspace_path=None):
    """Show statistics about the chat history"""
    exporter = CopilotChatExporter(workspace_path=workspace_path)
    sessions = exporter.extract_chat_history()
    
    if not sessions:
        print("No chat history found.")
        if exporter.workspace_id:
            print(f"Workspace ID: {exporter.workspace_id}")
        else:
            print(f"No workspace ID found for: {exporter.workspace_path}")
        return
    
    total_messages = sum(len(session.messages) for session in sessions)
    user_messages = sum(len([m for m in session.messages if m.role == 'user']) for session in sessions)
    assistant_messages = total_messages - user_messages
    
    print("📊 Chat History Statistics")
    print("=" * 30)
    print(f"Workspace: {workspace_path or 'current directory'}")
    if exporter.workspace_id:
        print(f"Workspace ID: {exporter.workspace_id}")
    print(f"Total Sessions: {len(sessions)}")
    print(f"Total Messages: {total_messages}")
    print(f"User Messages: {user_messages}")
    print(f"Assistant Messages: {assistant_messages}")
    
    if sessions:
        oldest_session = min(sessions, key=lambda s: s.created_at)
        newest_session = max(sessions, key=lambda s: s.updated_at)
        
        print(f"Oldest Session: {oldest_session.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Newest Session: {newest_session.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show session details
        print("\n📝 Session Details:")
        for i, session in enumerate(sessions, 1):
            msg_count = len(session.messages)
            print(f"  {i}. {session.title or session.session_id[:20]}... ({msg_count} messages)")


def main():
    """Main entry point"""
    workspace_path = None
    
    # Simple argument parsing
    if len(sys.argv) > 1:
        # Check if first argument is a command or a path
        first_arg = sys.argv[1].lower()
        
        if first_arg in ['stats', 'export', 'help']:
            command = first_arg
            # Check if workspace path is provided as second argument
            if len(sys.argv) > 2:
                workspace_path = sys.argv[2]
        elif first_arg.startswith('-'):
            # Handle flags
            if first_arg in ['-w', '--workspace'] and len(sys.argv) > 2:
                workspace_path = sys.argv[2]
                command = 'export'  # Default action
            else:
                command = 'help'
        else:
            # First argument is probably a workspace path
            workspace_path = sys.argv[1]
            command = 'export'  # Default action
        
        if command == 'stats':
            show_stats(workspace_path)
        elif command == 'export':
            quick_export(workspace_path)
        elif command == 'help':
            print("Copilot Chat Export Utility")
            print("\nUsage:")
            print("  python quick_export.py [workspace_path]")
            print("  python quick_export.py [command] [workspace_path]")
            print("\nCommands:")
            print("  export  - Export chat history to multiple formats (default)")
            print("  stats   - Show chat history statistics")
            print("  help    - Show this help message")
            print("\nOptions:")
            print("  -w, --workspace PATH  - Specify workspace path")
            print("\nExamples:")
            print("  python quick_export.py")
            print("  python quick_export.py C:\\path\\to\\workspace")
            print("  python quick_export.py stats")
            print("  python quick_export.py stats C:\\path\\to\\workspace")
            print("  python quick_export.py -w C:\\path\\to\\workspace")
        else:
            print(f"Unknown command: {command}")
            print("Use 'help' to see available commands")
    else:
        # Default action
        quick_export(workspace_path)


if __name__ == "__main__":
    main()
