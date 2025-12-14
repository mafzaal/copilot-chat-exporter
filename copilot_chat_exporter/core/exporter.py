"""
Main exporter class for Copilot Chat history.

This module handles extraction of chat history from VS Code's local storage
and exports it to various formats.
"""

import json
import sqlite3
import os
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import csv

from copilot_chat_exporter.core.models import ChatMessage, ChatSession


class CopilotChatExporter:
    """Main class for exporting Copilot chat history"""
    
    def __init__(self, workspace_path: Optional[str] = None):
        self.vscode_data_dir = self._find_vscode_data_directory()
        self.workspace_path = workspace_path or str(Path.cwd())
        self.workspace_id = None
        self.chat_db_path = None
        
        # Find workspace ID first, then look for database
        self.workspace_id = self._find_workspace_id()
        self._find_chat_database()
    
    def _find_vscode_data_directory(self) -> Path:
        """Find VS Code data directory based on the operating system"""
        if sys.platform == "win32":
            # Windows
            base_path = Path(os.environ.get("APPDATA", "")) / "Code"
        elif sys.platform == "darwin":
            # macOS
            base_path = Path.home() / "Library" / "Application Support" / "Code"
        else:
            # Linux
            base_path = Path.home() / ".config" / "Code"
        
        return base_path
    
    def _find_workspace_id(self) -> Optional[str]:
        """Find VS Code workspace ID for the given workspace path"""
        try:
            # Normalize the input folder path
            input_path = Path(self.workspace_path).resolve()
            normalized_input_path = input_path.as_posix().lower()
            print(f"Looking for workspace ID for: {self.workspace_path}")
            print(f"Normalized path: {normalized_input_path}")
            
            # Get workspace storage path
            workspace_storage_path = self.vscode_data_dir / "User" / "workspaceStorage"
            
            if not workspace_storage_path.exists():
                print(f"Workspace storage path does not exist: {workspace_storage_path}")
                return None
            
            print(f"Searching in workspace storage: {workspace_storage_path}")
            
            # Iterate through each workspace ID directory
            workspace_directories = list(workspace_storage_path.iterdir())
            print(f"Found {len(workspace_directories)} workspace directories to check")
            
            for directory in workspace_directories:
                if not directory.is_dir():
                    continue
                    
                workspace_id = directory.name
                workspace_json_path = directory / 'workspace.json'
                
                if workspace_json_path.exists():
                    try:
                        with open(workspace_json_path, 'r', encoding='utf-8') as f:
                            json_content = json.load(f)
                        
                        if json_content.get('folder'):
                            # Handle URL format workspace paths properly
                            workspace_folder_path = json_content['folder']
                            
                            # Remove file:// protocol prefix
                            if workspace_folder_path.startswith('file://'):
                                workspace_folder_path = workspace_folder_path[7:]  # Remove 'file://'
                            
                            # URL decode the path (handle %3a, %20, etc.)
                            workspace_folder_path = urllib.parse.unquote(workspace_folder_path)
                            
                            # Handle Windows paths that start with /c:/ pattern
                            if sys.platform == "win32" and workspace_folder_path.startswith('/') and ':' in workspace_folder_path:
                                # Remove leading slash for Windows paths like /c:/path
                                workspace_folder_path = workspace_folder_path[1:]
                            
                            # Normalize the workspace path for comparison
                            try:
                                workspace_path = Path(workspace_folder_path)
                                
                                # Skip remote paths (they won't resolve properly)
                                if workspace_folder_path.startswith(('vscode-remote://', 'wsl.localhost')):
                                    continue
                                
                                # Try to resolve the path, if it fails, use as-is
                                try:
                                    normalized_workspace_path = workspace_path.resolve().as_posix().lower()
                                except (OSError, ValueError):
                                    normalized_workspace_path = workspace_path.as_posix().lower()
                                
                                if normalized_workspace_path == normalized_input_path:
                                    print(f"✅ Found workspace ID: {workspace_id}")
                                    print(f"📁 Workspace path: {workspace_folder_path}")
                                    return workspace_id
                                    
                            except Exception as e:
                                print(f"Error normalizing workspace path '{workspace_folder_path}': {e}")
                                continue
                                
                    except Exception as e:
                        print(f"Error parsing workspace.json for ID {workspace_id}: {e}")
                        continue
            
            print("❌ Workspace ID not found for the specified folder path")
            return None
            
        except Exception as e:
            print(f"Error finding workspace ID: {e}")
            return None
    
    def _find_chat_database(self):
        """Find the Copilot chat database file"""
        # If we have a workspace ID, look in the specific workspace storage first
        if self.workspace_id:
            workspace_specific_path = self.vscode_data_dir / "User" / "workspaceStorage" / self.workspace_id
            print(f"🔍 Looking for chat database in workspace-specific storage: {workspace_specific_path}")
            
            if workspace_specific_path.exists():
                # Look for chat-related files in the workspace storage
                for db_file in workspace_specific_path.rglob("*"):
                    if db_file.is_file() and self._is_potential_chat_file(db_file):
                        if self._is_chat_database(db_file):
                            self.chat_db_path = db_file
                            print(f"✅ Found workspace-specific chat database: {db_file}")
                            return
        
        # Common locations for VS Code extensions data
        possible_paths = [
            self.vscode_data_dir / "User" / "workspaceStorage",
            self.vscode_data_dir / "User" / "globalStorage",
            self.vscode_data_dir / "CachedExtensions",
            # Check current workspace db folder
            Path("db"),
        ]
        
        for base_path in possible_paths:
            if base_path.exists():
                # Look for database files
                for db_file in base_path.rglob("*.db"):
                    if self._is_chat_database(db_file):
                        self.chat_db_path = db_file
                        print(f"Found chat database: {db_file}")
                        return
                
                # Look for SQLite files
                for db_file in base_path.rglob("*.sqlite*"):
                    if self._is_chat_database(db_file):
                        self.chat_db_path = db_file
                        print(f"Found chat database: {db_file}")
                        return
                
                # Look for vscdb files (VS Code database format)
                for db_file in base_path.rglob("*.vscdb"):
                    if self._is_chat_database(db_file):
                        self.chat_db_path = db_file
                        print(f"Found chat database: {db_file}")
                        return
    
    def _is_potential_chat_file(self, file_path: Path) -> bool:
        """Check if a file might contain chat data based on its name or extension"""
        filename = file_path.name.lower()
        extension = file_path.suffix.lower()
        
        # Check for common chat-related file patterns
        chat_patterns = [
            'chat', 'copilot', 'conversation', 'message', 'session',
            'github', 'ai', 'assistant', 'dialog'
        ]
        
        # Check for common database/data file extensions
        data_extensions = ['.db', '.sqlite', '.sqlite3', '.vscdb', '.json', '.data']
        
        # File might be chat-related if:
        # 1. Filename contains chat-related keywords
        # 2. Has a data file extension
        has_chat_keyword = any(pattern in filename for pattern in chat_patterns)
        has_data_extension = extension in data_extensions
        
        return has_chat_keyword or has_data_extension
    
    def _is_chat_database(self, db_path: Path) -> bool:
        """Check if a database file contains chat data"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Look for tables that might contain chat data
            chat_indicators = ['chat', 'message', 'conversation', 'copilot', 'session']
            
            for table in tables:
                if any(indicator in table.lower() for indicator in chat_indicators):
                    conn.close()
                    return True
            
            conn.close()
            return False
        except:
            return False
    
    def extract_chat_history(self) -> List[ChatSession]:
        """Extract chat history from the database"""
        if not self.chat_db_path or not self.chat_db_path.exists():
            print("Chat database not found. Trying alternative methods...")
            return self._extract_from_json_files()
        
        try:
            conn = sqlite3.connect(str(self.chat_db_path))
            cursor = conn.cursor()
            
            # Get table structure
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"Available tables: {tables}")
            
            sessions = []
            
            # Try to extract data from different table structures
            for table in tables:
                try:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [row[1] for row in cursor.fetchall()]
                    print(f"Table {table} columns: {columns}")
                    
                    # Try to extract messages
                    cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                    sample_data = cursor.fetchall()
                    
                    if sample_data:
                        print(f"Sample data from {table}: {sample_data[0] if sample_data else 'No data'}")
                        
                        # Process the data based on structure
                        sessions.extend(self._process_table_data(cursor, table, columns))
                
                except Exception as e:
                    print(f"Error processing table {table}: {e}")
                    continue
            
            conn.close()
            return sessions
            
        except Exception as e:
            print(f"Error reading database: {e}")
            return self._extract_from_json_files()
    
    def _process_table_data(self, cursor, table_name: str, columns: List[str]) -> List[ChatSession]:
        """Process data from a specific table"""
        sessions = []
        
        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            current_session = ChatSession(
                session_id=f"session_{datetime.now().isoformat()}",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            for row in rows:
                row_data = dict(zip(columns, row))
                
                # Try to extract message content
                content = None
                role = "unknown"
                timestamp = datetime.now()
                
                # Look for common field patterns
                for key, value in row_data.items():
                    key_lower = key.lower()
                    
                    if 'content' in key_lower or 'message' in key_lower or 'text' in key_lower:
                        if isinstance(value, str) and value.strip():
                            content = value
                    
                    if 'role' in key_lower or 'type' in key_lower or 'sender' in key_lower:
                        if isinstance(value, str):
                            role = value
                    
                    if 'time' in key_lower or 'date' in key_lower:
                        try:
                            if isinstance(value, (int, float)):
                                timestamp = datetime.fromtimestamp(value / 1000 if value > 1e10 else value)
                            elif isinstance(value, str):
                                timestamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        except:
                            pass
                
                if content:
                    message = ChatMessage(
                        id=f"msg_{len(current_session.messages)}",
                        timestamp=timestamp,
                        role=role,
                        content=content,
                        session_id=current_session.session_id,
                        metadata=row_data
                    )
                    current_session.messages.append(message)
            
            if current_session.messages:
                sessions.append(current_session)
            
        except Exception as e:
            print(f"Error processing table data: {e}")
        
        return sessions
    
    def _extract_from_json_files(self) -> List[ChatSession]:
        """Try to extract chat history from JSON files"""
        sessions = []
        
        # Look for JSON files in various locations
        search_paths = [
            self.vscode_data_dir / "User",
            Path("db"),
            Path("."),
        ]
        
        for path in search_paths:
            if path.exists():
                for json_file in path.rglob("*.json"):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            session = self._parse_json_data(data, json_file.name)
                            if session and session.messages:
                                sessions.append(session)
                    except:
                        continue
        
        return sessions
    
    def _parse_json_data(self, data: Any, filename: str) -> Optional[ChatSession]:
        """Parse JSON data to extract chat messages"""
        try:
            session = ChatSession(
                session_id=f"json_{filename}_{datetime.now().isoformat()}",
                title=f"Extracted from {filename}",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Try different JSON structures
            if isinstance(data, dict):
                self._extract_messages_from_dict(data, session)
            elif isinstance(data, list):
                self._extract_messages_from_list(data, session)
            
            return session if session.messages else None
            
        except Exception as e:
            print(f"Error parsing JSON data: {e}")
            return None
    
    def _extract_messages_from_dict(self, data: Dict, session: ChatSession):
        """Extract messages from dictionary structure"""
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and any(k in item for k in ['content', 'message', 'text']):
                        self._create_message_from_dict(item, session)
            elif isinstance(value, dict):
                self._extract_messages_from_dict(value, session)
    
    def _extract_messages_from_list(self, data: List, session: ChatSession):
        """Extract messages from list structure"""
        for item in data:
            if isinstance(item, dict):
                if any(k in item for k in ['content', 'message', 'text']):
                    self._create_message_from_dict(item, session)
                else:
                    self._extract_messages_from_dict(item, session)
    
    def _create_message_from_dict(self, item: Dict, session: ChatSession):
        """Create a message from dictionary item"""
        content = item.get('content') or item.get('message') or item.get('text', '')
        role = item.get('role', item.get('type', item.get('sender', 'unknown')))
        
        if content and isinstance(content, str) and content.strip():
            message = ChatMessage(
                id=f"msg_{len(session.messages)}",
                timestamp=datetime.now(),
                role=role,
                content=content.strip(),
                session_id=session.session_id,
                metadata=item
            )
            session.messages.append(message)
    
    def export_to_json(self, sessions: List[ChatSession], output_path: str):
        """Export chat history to JSON format"""
        data = {
            'exported_at': datetime.now().isoformat(),
            'total_sessions': len(sessions),
            'total_messages': sum(len(session.messages) for session in sessions),
            'sessions': [session.model_dump(mode='json') for session in sessions]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Exported {len(sessions)} sessions to {output_path}")
    
    def export_to_csv(self, sessions: List[ChatSession], output_path: str):
        """Export chat history to CSV format"""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Session ID', 'Session Title', 'Message ID', 'Timestamp', 'Role', 'Content'])
            
            for session in sessions:
                for message in session.messages:
                    writer.writerow([
                        session.session_id,
                        session.title or '',
                        message.id,
                        message.timestamp.isoformat(),
                        message.role,
                        message.content.replace('\n', '\\n')
                    ])
        
        print(f"Exported {sum(len(session.messages) for session in sessions)} messages to {output_path}")
    
    def export_to_markdown(self, sessions: List[ChatSession], output_path: str):
        """Export chat history to Markdown format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Copilot Chat History Export\n\n")
            f.write(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total Sessions: {len(sessions)}\n")
            f.write(f"Total Messages: {sum(len(session.messages) for session in sessions)}\n\n")
            
            for i, session in enumerate(sessions, 1):
                f.write(f"## Session {i}: {session.title or session.session_id}\n\n")
                f.write(f"**Created:** {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Messages:** {len(session.messages)}\n\n")
                
                for message in session.messages:
                    role_emoji = "🧑" if message.role == "user" else "🤖"
                    f.write(f"### {role_emoji} {message.role.title()}\n")
                    f.write(f"*{message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
                    f.write(f"{message.content}\n\n")
                    f.write("---\n\n")
        
        print(f"Exported {len(sessions)} sessions to {output_path}")
