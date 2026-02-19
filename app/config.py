import os

class AIConfig:
    """
    Configuración central de IA. 
    Prioriza Variables de Entorno (Repositorio GitHub / Cloud Run).
    """
    LLM_PROVIDER = "openai" # Hardcoded
    MODEL = "gpt-4o"        # Hardcoded
    TEMPERATURE = 0.2       # Hardcoded
    API_KEY = os.getenv("OPENAI_API_KEY") # Only API Key from Repo Variables

    @classmethod
    def get_masked_key(cls):
        if not cls.API_KEY:
            return "MISSING"
        return f"{cls.API_KEY[:8]}...{cls.API_KEY[-4:]}"

    @classmethod
    def print_summary(cls):
        print(f"🤖 [Config] Provider: {cls.LLM_PROVIDER}")
        print(f"🤖 [Config] Model: {cls.MODEL}")
        print(f"🤖 [Config] Temperature: {cls.TEMPERATURE}")
        print(f"🔑 [Config] API Key: {cls.get_masked_key()}")

config = AIConfig()
