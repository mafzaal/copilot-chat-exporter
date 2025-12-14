# Package Structure

This document describes the new organized package structure of the Copilot Chat Exporter.

## Directory Structure

```
copilot-chat-exporter/
├── copilot_chat_exporter/          # Main package
│   ├── __init__.py                 # Package initialization & public API
│   ├── config.py                   # Configuration settings
│   │
│   ├── core/                       # Core functionality
│   │   ├── __init__.py
│   │   ├── models.py               # Data models (ChatMessage, ChatSession)
│   │   └── exporter.py             # Main exporter class
│   │
│   ├── utils/                      # Utility functions
│   │   ├── __init__.py
│   │   └── workspace_finder.py     # VS Code workspace ID finder
│   │
│   └── cli/                        # Command-line interfaces
│       ├── __init__.py
│       ├── main.py                 # Main CLI with argparse
│       ├── quick_export.py         # Quick export utility
│       └── workspace_finder.py     # Workspace finder CLI
│
├── tests/                          # Test suite
│   ├── __init__.py
│   └── test_exporter.py            # Unit tests
│
├── main.py                         # Entry point script
├── pyproject.toml                  # Project configuration
└── README.md                       # Project documentation
```

## Module Organization

### Core Package (`copilot_chat_exporter/core/`)
- **models.py**: Pydantic data models
  - `ChatMessage`: Represents a single chat message
  - `ChatSession`: Represents a chat session with multiple messages

- **exporter.py**: Main exporter class
  - `CopilotChatExporter`: Handles extraction and export of chat history
  - Export formats: JSON, CSV, Markdown

### Utilities (`copilot_chat_exporter/utils/`)
- **workspace_finder.py**: VS Code workspace utilities
  - `VSCodeWorkspaceFinder`: Find and manage VS Code workspace IDs

### CLI (`copilot_chat_exporter/cli/`)
- **main.py**: Full-featured CLI with argparse
- **quick_export.py**: Quick export utility with minimal configuration
- **workspace_finder.py**: Standalone workspace finder tool

## Usage

### As a Package
```python
from copilot_chat_exporter import CopilotChatExporter

exporter = CopilotChatExporter()
sessions = exporter.extract_chat_history()
exporter.export_to_json(sessions, "output.json")
```

### Command Line Tools

After installing the package:
```bash
# Main CLI
copilot-chat-export --format json --output chat.json

# Quick export
copilot-chat-quick

# Workspace finder
copilot-workspace-finder --list
```

Or run directly:
```bash
# Main entry point
python main.py

# Run specific modules
python -m copilot_chat_exporter.cli.quick_export
python -m copilot_chat_exporter.cli.workspace_finder --list
```

### Run Directly from Git Repository

Use `uvx` to execute the tool directly from the GitHub repository without cloning:

```bash
# Quick export (default action)
uvx --from git+https://github.com/mafzaal/copilot-chat-exporter copilot-chat-quick

# Main CLI with options
uvx --from git+https://github.com/mafzaal/copilot-chat-exporter copilot-chat-export --format json

# Find workspace IDs
uvx --from git+https://github.com/mafzaal/copilot-chat-exporter copilot-workspace-finder --list

# Or run as module
uvx --from git+https://github.com/mafzaal/copilot-chat-exporter python -m copilot_chat_exporter.cli.quick_export
```

### Export Chat from Specific Workspace

By default, the tool uses the current directory as the workspace. To export chat history from a different workspace:

**Using the main CLI:**
```bash
# Specify workspace with --workspace or -w flag
python main.py --workspace /path/to/your/workspace --format json

# Example: Export to markdown format from specific workspace
python main.py -w ~/projects/my-app --format markdown -o my-app-chat.md
```

**Using quick export:**
```bash
# Pass workspace path as first argument
python -m copilot_chat_exporter.cli.quick_export /path/to/your/workspace

# Or use the -w flag
python -m copilot_chat_exporter.cli.quick_export -w /path/to/your/workspace

# Show statistics for specific workspace
python -m copilot_chat_exporter.cli.quick_export stats /path/to/your/workspace
```

**Using installed commands:**
```bash
# Main CLI
copilot-chat-export --workspace /path/to/your/workspace

# Quick export
copilot-chat-quick /path/to/your/workspace
```

**From Git repository:**
```bash
# Using uvx
uvx --from git+https://github.com/mafzaal/copilot-chat-exporter \
    copilot-chat-export --workspace /path/to/your/workspace --format json
```

**As a library:**
```python
from copilot_chat_exporter import CopilotChatExporter

# Specify workspace path
exporter = CopilotChatExporter(workspace_path="/path/to/your/workspace")
sessions = exporter.extract_chat_history()
exporter.export_to_json(sessions, "output.json")
```

**Finding your workspace path:**
```bash
# List all VS Code workspaces on your system
python -m copilot_chat_exporter.cli.workspace_finder --list

# Find workspace ID for a specific folder
python -m copilot_chat_exporter.cli.workspace_finder /path/to/folder

# With verbose output
python -m copilot_chat_exporter.cli.workspace_finder /path/to/folder --verbose
```


## Benefits of This Structure

1. **Clear Separation of Concerns**
   - Core logic separated from CLI
   - Models isolated in their own module
   - Utilities are reusable

2. **Better Imports**
   - Clean public API through `__init__.py`
   - Easy to import specific components
   - Prevents circular dependencies

3. **Easier Testing**
   - Tests organized in their own directory
   - Can easily test individual modules
   - Cleaner test imports

4. **Scalability**
   - Easy to add new exporters
   - New CLI tools can be added easily
   - Additional utilities can be added without clutter

5. **Professional Structure**
   - Follows Python packaging best practices
   - Ready for distribution via PyPI
   - Clear entry points defined in pyproject.toml
