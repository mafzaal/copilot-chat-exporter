# Copilot Chat History Exporter

This tool allows you to export your GitHub Copilot chat history from VS Code to various formats (JSON, CSV, Markdown). The tool can automatically find your VS Code workspace ID and search for workspace-specific chat data.

## Features

- 🔍 **Workspace ID Detection**: Automatically finds VS Code workspace IDs for specific folders
- 🗂️ **Workspace-Specific Search**: Prioritizes workspace-specific chat data
- 📄 **Multiple Formats**: Export to JSON, CSV, or Markdown
- 🎯 **Smart Parsing**: Handles different database structures and formats
- 📊 **Statistics**: View chat history statistics
- 🚀 **Easy to Use**: Simple command-line interface

## Quick Start

### Option 1: Quick Export (Recommended)
```bash
# Export from current workspace
python quick_export.py

# Export from specific workspace
python quick_export.py "C:\path\to\workspace"
```

This will automatically:
- Find your workspace ID
- Locate workspace-specific chat history
- Export to all formats (JSON, CSV, Markdown)
- Save files in the `exports/` directory

### Option 2: Custom Export
```bash
# Export from current workspace
python copilot_chat_exporter.py

# Export from specific workspace
python copilot_chat_exporter.py --workspace "C:\path\to\workspace"

# Export to specific format
python copilot_chat_exporter.py --workspace "C:\path\to\workspace" --format markdown --output my_chat_history.md

# Verbose output
python copilot_chat_exporter.py --workspace "C:\path\to\workspace" --format json --verbose
```

### Option 3: View Statistics
```bash
# Statistics for current workspace
python quick_export.py stats

# Statistics for specific workspace
python quick_export.py stats "C:\path\to\workspace"
```

### Option 4: Find Workspace ID Only
```bash
# Find workspace ID for current directory
python workspace_finder.py

# Find workspace ID for specific directory
python workspace_finder.py "C:\path\to\workspace"

# List all workspaces
python workspace_finder.py --list
```

## Installation

1. Make sure you have Python 3.8+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Or if using uv:
   ```bash
   uv sync
   ```

## Command Line Options

### copilot_chat_exporter.py
- `--format`: Export format (`json`, `csv`, `markdown`)
- `--output`: Output file path
- `--workspace`: Workspace path (default: current directory)
- `--verbose`: Show detailed output

### quick_export.py
- `export [workspace_path]`: Export to all formats (default)
- `stats [workspace_path]`: Show chat history statistics
- `help`: Show help message
- `-w, --workspace PATH`: Specify workspace path

### workspace_finder.py
- `folder_path`: Folder path to find workspace ID for (default: current directory)
- `--verbose, -v`: Show detailed output
- `--list, -l`: List all workspaces

## How It Works

1. **Workspace Detection**: The tool uses the same logic as VS Code to find workspace IDs by:
   - Scanning VS Code's workspace storage directory
   - Reading `workspace.json` files
   - Matching folder paths to find the correct workspace ID

2. **Chat Database Search**: Once the workspace ID is found, the tool:
   - First searches in workspace-specific storage
   - Falls back to global search locations
   - Looks for various file formats (SQLite, JSON, VS Code database files)

3. **Data Extraction**: The tool can extract chat data from:
   - SQLite databases
   - JSON configuration files
   - VS Code-specific database formats

## Output Formats

### JSON Format
```json
{
  "exported_at": "2024-01-15T10:30:00",
  "total_sessions": 5,
  "total_messages": 42,
  "sessions": [
    {
      "session_id": "session_123",
      "title": "Python Help",
      "created_at": "2024-01-15T09:00:00",
      "messages": [
        {
          "id": "msg_1",
          "timestamp": "2024-01-15T09:00:00",
          "role": "user",
          "content": "How do I create a list in Python?"
        }
      ]
    }
  ]
}
```

### CSV Format
Exports a flat structure with columns:
- Session ID
- Session Title  
- Message ID
- Timestamp
- Role
- Content

### Markdown Format
Creates a formatted document with:
- Export summary
- Sessions organized by title
- Messages with timestamps and role indicators
- Easy-to-read conversation flow

## Workspace ID Detection

The tool automatically detects VS Code workspace IDs by:

1. **Finding VS Code Data Directory**:
   - Windows: `%APPDATA%\Code\User\workspaceStorage`
   - macOS: `~/Library/Application Support/Code/User/workspaceStorage`
   - Linux: `~/.config/Code/User/workspaceStorage`

2. **Scanning Workspace Storage**: Each subdirectory represents a workspace with a unique ID

3. **Matching Paths**: Reads `workspace.json` files to match folder paths with workspace IDs

4. **Path Normalization**: Handles:
   - URL encoding (`%3A`, `%20`, etc.)
   - File protocol prefixes (`file://`)
   - Cross-platform path differences
   - Remote workspace paths (WSL, containers)

## Database Locations

The tool searches for chat databases in these locations (in order of priority):

1. **Workspace-Specific Storage**: `workspaceStorage/{workspace-id}/`
2. **Global Storage**: `Code/User/globalStorage/`
3. **Cached Extensions**: `Code/CachedExtensions/`
4. **Local Database**: `./db/`

## Example Usage

```bash
# Quick export from current workspace
uv run quick_export.py

# Export from specific workspace with verbose output
uv run copilot_chat_exporter.py --workspace "C:\MyProject" --format json --verbose

# View statistics for a workspace
uv run quick_export.py stats "C:\MyProject"

# Find workspace ID
uv run workspace_finder.py "C:\MyProject" --verbose

# List all VS Code workspaces
uv run workspace_finder.py --list

# Custom export with specific output file
uv run copilot_chat_exporter.py --workspace "C:\MyProject" --format markdown --output project_chats.md
```

## File Structure

```
.
├── copilot_chat_exporter.py    # Main exporter class
├── quick_export.py             # Quick export utility
├── workspace_finder.py         # Workspace ID finder utility
├── config.py                   # Configuration settings
├── test_exporter.py           # Test script
├── README.md                  # This file
└── exports/                   # Output directory (created automatically)
    ├── copilot_chat_workspace_20240115_103000.json
    ├── copilot_chat_workspace_20240115_103000.csv
    └── copilot_chat_workspace_20240115_103000.md
```

## Troubleshooting

### No Workspace ID Found
If the tool can't find your workspace ID:

1. **Verify Workspace**: Make sure the folder has been opened in VS Code
2. **Check Path**: Ensure the folder path is correct and accessible
3. **VS Code Version**: Make sure you're using a recent version of VS Code
4. **Manual Search**: Use `workspace_finder.py --list` to see all available workspaces

### No Chat History Found
If the tool can't find your chat history:

1. **Check Usage**: Ensure you've actually used Copilot Chat in that workspace
2. **Workspace Match**: Verify the correct workspace ID was found
3. **Database Location**: The chat database might be in a different location
4. **Permissions**: Make sure you have read permissions for VS Code's data directory

### Database Format Issues
If you encounter database reading issues:

1. **Close VS Code**: Ensure VS Code isn't locking the database files
2. **Check Permissions**: Verify read access to the database files
3. **Run with Verbose**: Use `--verbose` to see detailed error information

## Privacy Note

This tool only accesses your local chat history stored on your machine. No data is sent to external servers. The exported files contain your chat conversations, so handle them appropriately according to your privacy and security requirements.

## Dependencies

- `pydantic`: Data validation and serialization
- `python-dotenv`: Environment variable management
- `click`: Command-line interface utilities
- `rich`: Rich text and beautiful formatting
- Standard library modules: `sqlite3`, `json`, `csv`, `pathlib`, `datetime`, `urllib.parse`

## Contributing

Feel free to contribute improvements, bug fixes, or additional features. Some ideas for enhancement:

- [ ] Add date range filtering
- [ ] Add search functionality within chat content
- [ ] Support for different VS Code profiles
- [ ] Export to additional formats (HTML, PDF)
- [ ] Chat history analysis and insights
- [ ] GUI interface
- [ ] Integration with other editors (VS Code Insiders, Cursor, etc.)

## License

This tool is provided as-is for personal use. Make sure to comply with GitHub Copilot's terms of service when using this tool.
