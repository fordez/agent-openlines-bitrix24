
import os
import yaml
import sys

def get_secret(provider: str, key: str = "api_key"):
    """
    Busca un secreto priorizando:
    1. Variables de entorno (inyectadas por Cloud Run/Docker)
    2. mcp_agent.secrets.yaml (archivo local de secretos)
    """
    # 1. Intentar variable de entorno (ej: OPENAI_API_KEY)
    env_var_name = f"{provider.upper()}_API_KEY"
    env_val = os.getenv(env_var_name)
    if env_val:
        return env_val

    # 2. Intentar mcp_agent.secrets.yaml
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        secrets_path = os.path.join(base_dir, "mcp_agent.secrets.yaml")
        if os.path.exists(secrets_path):
            with open(secrets_path, "r") as f:
                secrets = yaml.safe_load(f)
                return secrets.get(provider, {}).get(key)
    except Exception as e:
        sys.stderr.write(f"⚠️ Error cargando secretos de yaml: {e}\n")

    return None
