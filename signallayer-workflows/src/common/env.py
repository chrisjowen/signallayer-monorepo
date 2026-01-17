"""Environment configuration utility."""

import os

from dotenv import load_dotenv


def setup_environment() -> None:
    """Load environment variables from .env files.
    
    Loads .env first (base configuration), then loads the file specified
    by DOTENV_FILE environment variable (e.g., .env.development) to override.
    
    This allows for a base .env with production settings, and environment-specific
    overrides in .env.development, .env.staging, etc.
    """
    # Load base .env first
    load_dotenv(".env", override=False)
    
    # Then load environment-specific file to override (if specified)
    env_file = os.getenv("DOTENV_FILE")
    if env_file and env_file != ".env":
        load_dotenv(env_file, override=True)

