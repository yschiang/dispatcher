import yaml

class ConfigValidationError(Exception):
    """Custom exception for configuration validation errors."""
    pass

def load_yaml(file_path: str):
    """Load the YAML configuration file."""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigValidationError(f"YAML Parsing Error: {str(e)}")
    except FileNotFoundError:
        raise ConfigValidationError(f"File not found: {file_path}")

def validate_service(service):
    """Validate a single service configuration."""
    required_fields = ["name", "uri", "default_upstream", "matches", "rules", "upstreams"]
    for field in required_fields:
        if field not in service:
            raise ConfigValidationError(f"Missing required field '{field}' in service {service.get('name', 'unknown')}")

    # Validate matches
    match_ids = set()
    for match in service["matches"]:
        if "id" not in match or "header_name" not in match or "operator" not in match or "value" not in match:
            raise ConfigValidationError(f"Invalid match definition in service {service['name']}: {match}")
        if match["id"] in match_ids:
            raise ConfigValidationError(f"Duplicate match ID '{match['id']}' in service {service['name']}")
        match_ids.add(match["id"])

    # Validate rules
    rule_ids = set()
    for rule in service["rules"]:
        if "id" not in rule or "matches" not in rule or "upstream_id" not in rule:
            raise ConfigValidationError(f"Invalid rule definition in service {service['name']}: {rule}")
        if rule["id"] in rule_ids:
            raise ConfigValidationError(f"Duplicate rule ID '{rule['id']}' in service {service['name']}")
        rule_ids.add(rule["id"])

        # Ensure all referenced matches exist
        for match_id in rule["matches"]:
            if match_id not in match_ids:
                raise ConfigValidationError(f"Rule '{rule['id']}' in service {service['name']} references undefined match ID '{match_id}'")

    # Validate upstreams
    upstream_ids = set()
    for upstream in service["upstreams"]:
        if "id" not in upstream or "target" not in upstream or "port" not in upstream:
            raise ConfigValidationError(f"Invalid upstream definition in service {service['name']}: {upstream}")
        if upstream["id"] in upstream_ids:
            raise ConfigValidationError(f"Duplicate upstream ID '{upstream['id']}' in service {service['name']}")
        upstream_ids.add(upstream["id"])

    # Ensure default_upstream exists in upstreams
    if service["default_upstream"] not in upstream_ids:
        raise ConfigValidationError(f"Default upstream '{service['default_upstream']}' in service {service['name']} does not exist in upstreams")

    # Validate rollstrategy
    rollstrategy = service.get("rollstrategy")
    if rollstrategy:
        if "groups" in rollstrategy:
            total_weight = 0
            expected_ids = [chr(i) for i in range(65, 65 + len(rollstrategy["groups"]))]  # Generate sequential IDs: A, B, C, ...
            actual_ids = [group["id"] for group in rollstrategy["groups"]]

            if actual_ids != expected_ids:
                raise ConfigValidationError(f"Rollstrategy group IDs in service {service['name']} are not in order. Expected: {expected_ids}, Found: {actual_ids}")

            for group in rollstrategy["groups"]:
                if "id" not in group or "upstream_id" not in group or "weight" not in group:
                    raise ConfigValidationError(f"Invalid group in rollstrategy for service {service['name']}: {group}")
                if group["upstream_id"] not in upstream_ids:
                    raise ConfigValidationError(f"Group upstream_id '{group['upstream_id']}' in rollstrategy for service {service['name']} does not exist in upstreams")
                total_weight += group["weight"]
            if total_weight != 100:
                raise ConfigValidationError(f"Total weight of rollstrategy in service {service['name']} must equal 100, but got {total_weight}")
        else:
            # If rollstrategy exists but no groups, default_upstream should be valid
            if service["default_upstream"] not in upstream_ids:
                raise ConfigValidationError(f"Rollstrategy in service {service['name']} does not define groups, and default_upstream '{service['default_upstream']}' is invalid")

def validate_config(config):
    """Validate the entire configuration file."""
    if "services" not in config:
        raise ConfigValidationError("Missing 'services' section in configuration")

    for service in config["services"]:
        validate_service(service)

def load_and_validate_config(file_path: str):
    """Load and validate the configuration."""
    config = load_yaml(file_path)
    validate_config(config)
    return config