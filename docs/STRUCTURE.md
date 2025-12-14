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
