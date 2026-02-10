# Bot Viajes 🤖✈️

Bot de asistencia virtual de viajes para Bitrix24 Open Lines, impulsado por **Gemini** via **mcp-agent**.

## Estructura del Proyecto

```
bot-viajes/
├── main.py                    # Servidor FastAPI (punto de entrada)
├── app/                       # Lógica principal
│   ├── auth.py                # Autenticación con Bitrix24 (OAuth)
│   ├── bitrix.py              # Parseo de eventos + envío de respuestas
│   └── gemini_agent.py        # Agente AI con mcp-agent + Gemini
├── tools/                     # Scripts CLI de utilidad
│   └── send_message.py        # Enviar mensaje manual al bot
├── testing/                   # Scripts de administración del bot
│   ├── register_bot.py        # Registrar bot en Bitrix24
│   ├── update_bot.py          # Actualizar URL del bot
│   ├── delete_bot.py          # Eliminar bot
│   ├── get_bot_info.py        # Ver info del bot
│   ├── check_bindings.py      # Ver event bindings
│   ├── check_open_lines.py    # Ver líneas abiertas
│   ├── bind_bot_to_line.py    # Vincular bot a canal
│   └── bind_event.py          # Vincular eventos
├── mcp_agent.config.yaml      # Config de mcp-agent
├── mcp_agent.secrets.yaml     # Secrets (gitignored)
├── .env                       # Variables de entorno (gitignored)
└── .gitignore
```

## Requisitos

```bash
pip install fastapi uvicorn "mcp-agent[google]" python-dotenv requests
```

## Configuración

1. Copia `.env.example` a `.env` y configura tus credenciales de Bitrix24 y `GOOGLE_API_KEY`
2. Configura `mcp_agent.secrets.yaml` con tu API key de Google
3. Expón el servidor con ngrok: `ngrok http 8000`
4. Actualiza la URL del webhook: `python testing/update_bot.py`

## Ejecución

```bash
python main.py
```

El servidor escuchará en `http://0.0.0.0:8000` y procesará automáticamente los mensajes de Bitrix24 con Gemini.
