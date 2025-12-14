"""Configuration settings for Copilot Chat Exporter."""

# Export settings
EXPORT_FORMAT = "json"  # Options: json, csv, markdown
OUTPUT_DIRECTORY = "exports"
INCLUDE_METADATA = True
VERBOSE_OUTPUT = True

# Database search paths (add custom paths here)
CUSTOM_DB_PATHS = [
    # Add any custom paths where your chat database might be located
    # Example: "C:\\Custom\\Path\\To\\Chat\\Database"
]

# Export filters
FILTER_BY_DATE = False
START_DATE = "2024-01-01"
END_DATE = "2024-12-31"

FILTER_BY_ROLE = False
INCLUDE_ROLES = ["user", "assistant"]  # Options: user, assistant

# Output formatting
MAX_MESSAGE_LENGTH = None  # Set to limit message length in export
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
