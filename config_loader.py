from config_validator import load_yaml, validate_config, ConfigValidationError

def load_and_validate_config(file_path: str):
    """Load and validate the configuration."""
    try:
        # Load the configuration
        config = load_yaml(file_path)
        
        # Validate the configuration
        validate_config(config)
        
        return config
    except ConfigValidationError as e:
        raise ConfigValidationError(f"Configuration validation failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error occurred while loading configuration: {str(e)}")
