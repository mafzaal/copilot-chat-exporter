#!/usr/bin/env python3
"""
VS Code Workspace ID Finder CLI
"""

import sys
import argparse
from pathlib import Path

from copilot_chat_exporter.utils.workspace_finder import VSCodeWorkspaceFinder


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Find VS Code Workspace ID')
    parser.add_argument('folder_path', nargs='?', default='.', 
                       help='Folder path to find workspace ID for (default: current directory)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Show detailed output')
    parser.add_argument('--list', '-l', action='store_true', 
                       help='List all workspaces')
    
    args = parser.parse_args()
    
    finder = VSCodeWorkspaceFinder()
    
    if args.list:
        print("📋 All VS Code Workspaces:")
        print("=" * 50)
        
        workspaces = finder.list_all_workspaces()
        
        if not workspaces:
            print("No workspaces found.")
            return
        
        for i, workspace in enumerate(workspaces, 1):
            status = "✅ exists" if workspace['exists'] else "❌ missing"
            print(f"{i:2d}. {workspace['id']}")
            print(f"    📁 {workspace['path']} ({status})")
            print()
        
        print(f"Total: {len(workspaces)} workspaces")
        return
    
    # Find workspace ID for specific folder
    folder_path = Path(args.folder_path).resolve()
    
    print(f"🔍 Finding workspace ID for: {folder_path}")
    
    workspace_id = finder.find_workspace_id(str(folder_path), verbose=args.verbose)
    
    if workspace_id:
        print(f"✅ Workspace ID found: {workspace_id}")
    else:
        print("❌ Workspace ID not found")
        print("\nPossible reasons:")
        print("• This folder hasn't been opened in VS Code")
        print("• VS Code hasn't been run on this system")
        print("• The folder path has changed since it was last opened")
        sys.exit(1)


if __name__ == "__main__":
    main()
