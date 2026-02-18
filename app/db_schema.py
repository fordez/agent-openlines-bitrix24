import os

# Environment Configuration
# Defaults to production (no prefix) unless APP_ENV is set to 'test'
ENV_PREFIX = "test_" if os.getenv("APP_ENV") == "test" else ""

class Collections:
    AGENTS = f"{ENV_PREFIX}agents"
    METRICS = f"{ENV_PREFIX}metrics"
    INSTALLATIONS = f"{ENV_PREFIX}installations"
    CONFIG_APP = f"{ENV_PREFIX}config-app"
    CONFIG_SECRETS = f"{ENV_PREFIX}config-secrets"
    CONFIG_AI = f"{ENV_PREFIX}config-ai"
    CONFIG_ARCHITECT = f"{ENV_PREFIX}config-architect"
    SESSIONS = f"{ENV_PREFIX}sessions"
    AUDIT_LOGS = f"{ENV_PREFIX}audit_logs"
    
    # Sub-collections (usually no prefix, but kept here for reference)
    MESSAGES = "messages"
    KNOWLEDGE = "knowledge"
