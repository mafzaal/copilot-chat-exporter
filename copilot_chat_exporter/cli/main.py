#!/usr/bin/env python3
"""
Main CLI entry point for Copilot Chat Exporter
"""

import argparse
from datetime import datetime
from pathlib import Path

from copilot_chat_exporter.core.exporter import CopilotChatExporter


def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description='Export Copilot Chat History')
    parser.add_argument('--format', choices=['json', 'csv', 'markdown'], default='json',
                       help='Export format (default: json)')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--workspace', '-w', help='Workspace path (default: current directory)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Set default output filename based on format
    if not args.output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        workspace_name = Path(args.workspace or Path.cwd()).name
        args.output = f"copilot_chat_{workspace_name}_{timestamp}.{args.format}"
    
    exporter = CopilotChatExporter(workspace_path=args.workspace)
    
    print("Extracting chat history...")
    sessions = exporter.extract_chat_history()
    
    if not sessions:
        print("No chat history found. This could be because:")
        print("1. Copilot chat database is in a different location")
        print("2. Chat history is stored in a different format")
        print("3. No chat history exists yet")
        print("4. The workspace ID could not be found")
        if exporter.workspace_id:
            print(f"   Workspace ID found: {exporter.workspace_id}")
        else:
            print(f"   No workspace ID found for: {exporter.workspace_path}")
        return
    
    print(f"Found {len(sessions)} chat sessions with {sum(len(s.messages) for s in sessions)} total messages")
    if exporter.workspace_id:
        print(f"Workspace ID: {exporter.workspace_id}")
    
    # Export based on format
    if args.format == 'json':
        exporter.export_to_json(sessions, args.output)
    elif args.format == 'csv':
        exporter.export_to_csv(sessions, args.output)
    elif args.format == 'markdown':
        exporter.export_to_markdown(sessions, args.output)
    
    if args.verbose:
        for session in sessions:
            print(f"Session: {session.session_id}")
            print(f"  Title: {session.title}")
            print(f"  Messages: {len(session.messages)}")
            for msg in session.messages[:3]:  # Show first 3 messages
                print(f"    {msg.role}: {msg.content[:100]}...")


if __name__ == "__main__":
    main()
