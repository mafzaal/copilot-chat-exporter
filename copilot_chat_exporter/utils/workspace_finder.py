"""
VS Code Workspace ID Finder

This module finds the VS Code workspace ID for a given folder path.
"""

import json
import sys
import urllib.parse
from pathlib import Path
from typing import Optional, List, Dict


class VSCodeWorkspaceFinder:
    """Find VS Code workspace IDs"""
    
    def __init__(self):
        self.vscode_data_dir = self._find_vscode_data_directory()
    
    def _find_vscode_data_directory(self) -> Path:
        """Find VS Code data directory based on the operating system"""
        if sys.platform == "win32":
            # Windows
            import os
            base_path = Path(os.environ.get("APPDATA", "")) / "Code"
        elif sys.platform == "darwin":
            # macOS
            base_path = Path.home() / "Library" / "Application Support" / "Code"
        else:
            # Linux
            base_path = Path.home() / ".config" / "Code"
        
        return base_path
    
    def find_workspace_id(self, folder_path: str, verbose: bool = False) -> Optional[str]:
        """Find VS Code workspace ID for the given folder path"""
        try:
            # Normalize the input folder path
            input_path = Path(folder_path).resolve()
            # Convert to forward slashes and lowercase for consistent comparison
            normalized_input_path = input_path.as_posix().lower()
            
            if verbose:
                print(f"🔍 Looking for workspace ID for: {folder_path}")
                print(f"📁 Normalized path: {normalized_input_path}")
            
            # Get workspace storage path
            workspace_storage_path = self.vscode_data_dir / "User" / "workspaceStorage"
            
            if not workspace_storage_path.exists():
                if verbose:
                    print(f"❌ Workspace storage path does not exist: {workspace_storage_path}")
                    print("   Make sure VS Code has been run at least once on this system.")
                return None
            
            if verbose:
                print(f"🗂️  Searching in workspace storage: {workspace_storage_path}")
            
            # Iterate through each workspace ID directory
            workspace_directories = list(workspace_storage_path.iterdir())
            
            if verbose:
                print(f"📊 Found {len(workspace_directories)} workspace directories to check")
            
            for directory in workspace_directories:
                if not directory.is_dir():
                    continue
                    
                workspace_id = directory.name
                workspace_json_path = directory / 'workspace.json'
                
                if verbose:
                    print(f"🔎 Checking workspace ID: {workspace_id}")
                
                if workspace_json_path.exists():
                    if verbose:
                        print(f"📄 Found workspace.json for ID: {workspace_id}")
                    
                    try:
                        with open(workspace_json_path, 'r', encoding='utf-8') as f:
                            json_content = json.load(f)
                        
                        if json_content.get('folder'):
                            # Handle URL format workspace paths properly
                            workspace_folder_path = json_content['folder']
                            
                            if verbose:
                                print(f"   Raw workspace path from JSON: {workspace_folder_path}")
                            
                            # Remove file:// protocol prefix
                            if workspace_folder_path.startswith('file://'):
                                workspace_folder_path = workspace_folder_path[7:]  # Remove 'file://'
                            
                            # URL decode the path (handle %3a, %20, etc.)
                            workspace_folder_path = urllib.parse.unquote(workspace_folder_path)
                            
                            # Handle Windows paths that start with /c:/ pattern
                            if sys.platform == "win32" and workspace_folder_path.startswith('/') and ':' in workspace_folder_path:
                                # Remove leading slash for Windows paths like /c:/path
                                workspace_folder_path = workspace_folder_path[1:]
                            
                            if verbose:
                                print(f"   Processed workspace path: {workspace_folder_path}")
                            
                            # Normalize the workspace path for comparison
                            try:
                                workspace_path = Path(workspace_folder_path)
                                
                                # Skip remote paths (they won't resolve properly)
                                if workspace_folder_path.startswith(('vscode-remote://', 'wsl.localhost')):
                                    if verbose:
                                        print(f"   Skipping remote path: {workspace_folder_path}")
                                    continue
                                
                                # Try to resolve the path, if it fails, use as-is
                                try:
                                    normalized_workspace_path = workspace_path.resolve().as_posix().lower()
                                except (OSError, ValueError):
                                    # If resolve fails, just normalize the string representation
                                    normalized_workspace_path = workspace_path.as_posix().lower()
                                
                                if verbose:
                                    print(f"   Normalized workspace path: {normalized_workspace_path}")
                                
                                if normalized_workspace_path == normalized_input_path:
                                    if verbose:
                                        print(f"✅ Match found!")
                                    return workspace_id
                                    
                            except Exception as e:
                                if verbose:
                                    print(f"⚠️  Error normalizing workspace path '{workspace_folder_path}': {e}")
                                continue
                        else:
                            if verbose:
                                print(f"   No folder property found in workspace.json")
                                
                    except Exception as e:
                        if verbose:
                            print(f"⚠️  Error parsing workspace.json for ID {workspace_id}: {e}")
                        continue
                else:
                    if verbose:
                        print(f"   No workspace.json found for ID: {workspace_id}")
            
            if verbose:
                print("❌ Workspace ID not found for the specified folder path")
            return None
            
        except Exception as e:
            if verbose:
                print(f"❌ Error finding workspace ID: {e}")
            return None
    
    def list_all_workspaces(self) -> List[Dict[str, str]]:
        """List all VS Code workspaces"""
        workspaces = []
        
        workspace_storage_path = self.vscode_data_dir / "User" / "workspaceStorage"
        
        if not workspace_storage_path.exists():
            return workspaces
        
        for directory in workspace_storage_path.iterdir():
            if not directory.is_dir():
                continue
                
            workspace_id = directory.name
            workspace_json_path = directory / 'workspace.json'
            
            if workspace_json_path.exists():
                try:
                    with open(workspace_json_path, 'r', encoding='utf-8') as f:
                        json_content = json.load(f)
                    
                    if json_content.get('folder'):
                        workspace_folder_path = json_content['folder']
                        
                        # Remove file:// protocol prefix
                        if workspace_folder_path.startswith('file://'):
                            workspace_folder_path = workspace_folder_path[7:]
                        
                        # URL decode the path
                        workspace_folder_path = urllib.parse.unquote(workspace_folder_path)
                        
                        workspaces.append({
                            'id': workspace_id,
                            'path': workspace_folder_path,
                            'exists': Path(workspace_folder_path).exists()
                        })
                        
                except Exception:
                    continue
        
        return workspaces
