"""
Moltbot Configuration Builder
Modular configuration management for OpenClaw Gateway
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Constants
MOLTBOT_PORT = 18789
CONFIG_DIR = os.path.expanduser("~/.openclaw")
CONFIG_FILE = os.path.join(CONFIG_DIR, "openclaw.json")
WORKSPACE_DIR = os.path.expanduser("~/clawd")


def generate_token() -> str:
    """Generate a secure random token"""
    import secrets
    return secrets.token_hex(32)


def ensure_directories():
    """Ensure required directories exist"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(WORKSPACE_DIR, exist_ok=True)


def load_existing_config() -> Dict[str, Any]:
    """Load existing configuration file if present"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load existing config: {e}")
    return {}


def get_or_generate_token(
    existing_config: Dict[str, Any],
    provided_token: Optional[str],
    force_new: bool
) -> str:
    """
    Get existing token, use provided token, or generate new one
    
    Args:
        existing_config: Current configuration
        provided_token: Token provided by caller
        force_new: Force generation of new token
        
    Returns:
        Token to use
    """
    if force_new:
        return generate_token()
    
    # Try to reuse existing token
    try:
        existing_token = existing_config.get("gateway", {}).get("auth", {}).get("token")
        if existing_token:
            return existing_token
    except Exception:
        pass
    
    # Use provided token or generate new
    return provided_token or generate_token()


def build_gateway_config(token: str) -> Dict[str, Any]:
    """Build gateway configuration section"""
    return {
        "mode": "local",
        "port": MOLTBOT_PORT,
        "bind": "lan",
        "auth": {
            "mode": "token",
            "token": token
        },
        "controlUi": {
            "enabled": True,
            "allowInsecureAuth": True
        }
    }


def ensure_base_structure(config: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure basic configuration structure exists"""
    if "models" not in config:
        config["models"] = {"mode": "merge", "providers": {}}
    
    config["models"]["mode"] = "merge"
    
    if "providers" not in config["models"]:
        config["models"]["providers"] = {}
    
    if "agents" not in config:
        config["agents"] = {"defaults": {}}
    
    if "defaults" not in config["agents"]:
        config["agents"]["defaults"] = {}
    
    config["agents"]["defaults"]["workspace"] = WORKSPACE_DIR
    
    return config


def build_emergent_gpt_provider(api_key: str, base_url: str) -> Dict[str, Any]:
    """Build Emergent GPT provider configuration"""
    return {
        "baseUrl": f"{base_url}/",
        "apiKey": api_key,
        "api": "openai-completions",
        "models": [
            {
                "id": "gpt-5.2",
                "name": "GPT-5.2",
                "reasoning": True,
                "input": ["text"],
                "cost": {
                    "input": 0.00000175,
                    "output": 0.000014,
                    "cacheRead": 0.000000175,
                    "cacheWrite": 0.00000175
                },
                "contextWindow": 400000,
                "maxTokens": 128000
            }
        ]
    }


def build_emergent_claude_provider(api_key: str, base_url: str) -> Dict[str, Any]:
    """Build Emergent Claude provider configuration"""
    return {
        "baseUrl": base_url,
        "apiKey": api_key,
        "api": "anthropic-messages",
        "authHeader": True,
        "models": [
            {
                "id": "claude-sonnet-4-6",
                "name": "Claude Sonnet 4.6",
                "input": ["text"],
                "cost": {
                    "input": 0.000003,
                    "output": 0.000015,
                    "cacheRead": 0.0000003,
                    "cacheWrite": 0.00000375
                },
                "contextWindow": 200000,
                "maxTokens": 64000
            },
            {
                "id": "claude-opus-4-6",
                "name": "Claude Opus 4.6",
                "input": ["text"],
                "cost": {
                    "input": 0.000005,
                    "output": 0.000025,
                    "cacheRead": 0.0000005,
                    "cacheWrite": 0.00000625
                },
                "contextWindow": 200000,
                "maxTokens": 64000
            }
        ]
    }


def configure_emergent_provider(
    config: Dict[str, Any],
    api_key: Optional[str]
) -> Dict[str, Any]:
    """Configure Emergent LLM provider"""
    emergent_key = api_key or os.environ.get('EMERGENT_API_KEY', 'sk-emergent-1234')
    emergent_base_url = os.environ.get(
        'EMERGENT_BASE_URL',
        'https://integrations.emergentagent.com/llm'
    )
    
    # Add GPT provider
    config["models"]["providers"]["emergent-gpt"] = build_emergent_gpt_provider(
        emergent_key,
        emergent_base_url
    )
    
    # Add Claude provider
    config["models"]["providers"]["emergent-claude"] = build_emergent_claude_provider(
        emergent_key,
        emergent_base_url
    )
    
    # Set model aliases and defaults
    config["agents"]["defaults"]["models"] = {
        "emergent-gpt/gpt-5.2": {"alias": "gpt-5.2"},
        "emergent-claude/claude-sonnet-4-6": {"alias": "sonnet"},
        "emergent-claude/claude-opus-4-6": {"alias": "opus"}
    }
    
    config["agents"]["defaults"]["model"] = {
        "primary": "emergent-claude/claude-opus-4-6"
    }
    
    return config


def build_openai_provider(api_key: str) -> Dict[str, Any]:
    """Build OpenAI provider configuration"""
    return {
        "baseUrl": "https://api.openai.com/v1/",
        "apiKey": api_key,
        "api": "openai-completions",
        "models": [
            {
                "id": "gpt-5.2",
                "name": "GPT-5.2",
                "reasoning": True,
                "input": ["text", "image"],
                "cost": {
                    "input": 0.00000175,
                    "output": 0.000014,
                    "cacheRead": 0.000000175,
                    "cacheWrite": 0.00000175
                },
                "contextWindow": 400000,
                "maxTokens": 128000
            },
            {
                "id": "o4-mini-2025-04-16",
                "name": "o4-mini",
                "reasoning": True,
                "input": ["text", "image"],
                "cost": {
                    "input": 0.0000011,
                    "output": 0.0000044
                },
                "contextWindow": 200000,
                "maxTokens": 100000
            },
            {
                "id": "gpt-4o",
                "name": "GPT-4o",
                "reasoning": False,
                "input": ["text", "image"],
                "cost": {
                    "input": 0.0000025,
                    "output": 0.00001
                },
                "contextWindow": 128000,
                "maxTokens": 16384
            }
        ]
    }


def configure_openai_provider(
    config: Dict[str, Any],
    api_key: str
) -> Dict[str, Any]:
    """Configure OpenAI provider"""
    config["models"]["providers"]["openai"] = build_openai_provider(api_key)
    
    config["agents"]["defaults"]["models"] = {
        "openai/gpt-5.2": {"alias": "gpt-5.2"}
    }
    
    config["agents"]["defaults"]["model"] = {
        "primary": "openai/gpt-5.2"
    }
    
    return config


def build_anthropic_provider(api_key: str) -> Dict[str, Any]:
    """Build Anthropic provider configuration"""
    return {
        "baseUrl": "https://api.anthropic.com",
        "apiKey": api_key,
        "api": "anthropic-messages",
        "models": [
            {
                "id": "claude-opus-4-5-20251101",
                "name": "Claude Opus 4.5",
                "input": ["text", "image"],
                "cost": {
                    "input": 0.000015,
                    "output": 0.000075,
                    "cacheRead": 0.0000015,
                    "cacheWrite": 0.00001875
                },
                "contextWindow": 200000,
                "maxTokens": 64000
            }
        ]
    }


def configure_anthropic_provider(
    config: Dict[str, Any],
    api_key: str
) -> Dict[str, Any]:
    """Configure Anthropic provider"""
    config["models"]["providers"]["anthropic"] = build_anthropic_provider(api_key)
    
    config["agents"]["defaults"]["models"] = {
        "anthropic/claude-opus-4-5-20251101": {"alias": "opus"}
    }
    
    config["agents"]["defaults"]["model"] = {
        "primary": "anthropic/claude-opus-4-5-20251101"
    }
    
    return config


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    logger.info(f"Updated Moltbot config at {CONFIG_FILE}")


def create_moltbot_config(
    token: Optional[str] = None,
    api_key: Optional[str] = None,
    provider: str = "emergent",
    force_new_token: bool = False
) -> str:
    """
    Update openclaw.json with gateway config and provider settings
    
    Args:
        token: Optional token. If not provided, reuses existing or generates new.
        api_key: Optional API key for provider.
        provider: The LLM provider - "emergent", "openai", or "anthropic".
        force_new_token: If True, always generates a new token (triggers gateway restart).
        
    Returns:
        The token being used (existing or new).
    """
    # Ensure directories exist
    ensure_directories()
    
    # Load existing configuration
    config = load_existing_config()
    
    # Get or generate token
    final_token = get_or_generate_token(config, token, force_new_token)
    
    logger.info(
        f"Config token: {'new token' if force_new_token else 'reusing/provided'}, "
        f"provider: {provider}"
    )
    
    # Build gateway configuration
    config["gateway"] = build_gateway_config(final_token)
    
    # Ensure base structure
    config = ensure_base_structure(config)
    
    # Configure provider
    if provider == "emergent":
        config = configure_emergent_provider(config, api_key)
    elif provider == "openai":
        if not api_key:
            raise ValueError("OpenAI provider requires an API key")
        config = configure_openai_provider(config, api_key)
    elif provider == "anthropic":
        if not api_key:
            raise ValueError("Anthropic provider requires an API key")
        config = configure_anthropic_provider(config, api_key)
    else:
        raise ValueError(f"Unknown provider: {provider}")
    
    # Save configuration
    save_config(config)
    
    return final_token
