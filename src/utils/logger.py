import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme

# Emoji mapping for different log levels
EMOJI_MAP = {
    'DEBUG': '🐛',
    'INFO': 'ℹ️',
    'WARNING': '⚠️',
    'ERROR': '❌',
    'CRITICAL': '💥'
}

# Custom theme for the logger
custom_theme = Theme({
    "debug": "dim cyan",
    "info": "green",
    "warning": "yellow",
    "error": "bold red",
    "critical": "bold underline red",
})

# Set up the console with the custom theme
console = Console(theme=custom_theme)


class EmojiFormatter(logging.Formatter):
    """Custom formatter to add emojis based on the log level."""

    def format(self, record):
        # Get the emoji for the log level
        emoji = EMOJI_MAP.get(record.levelname, '')
        # Add the emoji to the message
        record.msg = f"{emoji} {record.msg}"
        return super().format(record)


def setup_logger(name="app_logger", level=logging.INFO):
    """Sets up a logger with RichHandler for rich output, including colors and emojis."""
    # Create a logger
    logger = logging.getLogger(name)

    # Set the logging level
    logger.setLevel(level)

    # If the logger already has handlers, skip adding another one
    if not logger.handlers:
        # Create a RichHandler with our custom console
        rich_handler = RichHandler(console=console, rich_tracebacks=True)

        # Custom formatting
        log_format = "%(message)s"
        formatter = EmojiFormatter(log_format)

        # Apply the custom formatter
        rich_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(rich_handler)

    return logger


if __name__ == "__main__":
    logger = setup_logger(level=logging.DEBUG)

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
