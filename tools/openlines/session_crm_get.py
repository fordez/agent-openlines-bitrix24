from app.auth import call_bitrix_method
import sys
import json

async def session_crm_get(chat_id: int, access_token: str = None, domain: str = None) -> str:
    """
    Verifica si la sesión de chat actual ya tiene un CRM (Lead/Deal) vinculado.
    Usa imopenlines.dialog.get y parsea entity_data_2.
    """
    sys.stderr.write(f"  🔍 Tool session_crm_get: chat_id={chat_id}\n")

    try:
        params = {
            "CHAT_ID": chat_id
        }

        # imopenlines.session.crm.get NO existe o no es accesible.
        # Usamos imopenlines.dialog.get que contiene la misma info en metadatos.
        result = await call_bitrix_method("imopenlines.dialog.get", params, access_token=access_token, domain=domain)
        
        data = result.get("result")
        
        if not data:
             return "No se pudo obtener información del diálogo."

        # Buscamos en entity_data_2 (formato: LEAD|0|COMPANY|0|CONTACT|51908|DEAL|10378)
        entity_data = data.get("entity_data_2", "")
        sys.stderr.write(f"  📊 Raw entity_data_2: {entity_data}\n")
        
        crm_info = {}
        if entity_data:
            parts = entity_data.split("|")
            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    key = parts[i]
                    val = parts[i+1]
                    if val != "0":
                        crm_info[key] = val
        
        if not crm_info:
            return "No hay CRM (Lead/Deal/Contacto) vinculado a esta sesión."
        
        return f"CRM VINCULADO: {json.dumps(crm_info)}"

    except Exception as e:
        sys.stderr.write(f"  ❌ Error en session_crm_get: {e}\n")
        return f"Error verificando CRM de sesión: {e}"
