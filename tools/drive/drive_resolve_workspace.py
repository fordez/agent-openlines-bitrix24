"""
Tool to resolve or create a dedicated workspace folder for a CRM identity (Lead/Contact/Deal).
Ensures that the bot only works within the "Domain of Identity".
"""
from app.auth import call_bitrix_method
import sys

async def drive_resolve_workspace(entity_id: int, entity_type: str, entity_name: str = "Reserva") -> str:
    """
    Obtiene o crea el ID de la carpeta dedicada para el cliente actual.
    Garantiza que el bot trabaje solo dentro del 'Dominio de la Identidad'.
    
    Args:
        entity_id: ID del Lead, Contact o Deal.
        entity_type: Tipo (LEAD, CONTACT, DEAL).
        entity_name: Nombre para la carpeta (ej: el nombre del cliente).
    """
    if not entity_id or not entity_type:
        return "Error: entity_id y entity_type son necesarios."

    try:
        # 1. Obtener almacenamiento raíz (Common Drive)
        storage_res = await call_bitrix_method("disk.storage.getlist", {})
        storages = storage_res.get("result", [])
        if not storages:
            return "Error: No se encontró almacenamiento en el Drive."
        
        root_id = storages[0].get("ROOT_OBJECT_ID")
        
        # 2. Buscar o Crear carpeta de la IDENTIDAD específica directamente en la raíz
        # Formato: [TIPO]_[ID]_[NOMBRE]
        folder_name = f"{entity_type.upper()}_{entity_id}_{entity_name}".strip()
        
        # Primero buscamos por prefijo [TIPO]_[ID] para evitar duplicados si el nombre cambia
        search_prefix = f"{entity_type.upper()}_{entity_id}_"
        existing = await call_bitrix_method("disk.folder.getchildren", {
            "id": root_id,
            "filter": {"%NAME": search_prefix}
        })
        
        if existing.get("result"):
            workspace_id = existing["result"][0]["ID"]
            return f"Workspace identificado: ID {workspace_id} (Carpeta: {existing['result'][0]['NAME']})"
        else:
            # Crear nueva carpeta de identidad directamente en el root
            new_workspace = await call_bitrix_method("disk.folder.addsubfolder", {
                "id": root_id,
                "data": {"NAME": folder_name}
            })
            workspace_id = new_workspace.get("result", {}).get("ID")
            return f"Nuevo workspace creado para la identidad: ID {workspace_id} (Carpeta: {folder_name})"

    except Exception as e:
        sys.stderr.write(f"  ❌ Error en drive_resolve_workspace: {e}\n")
        return f"Error al resolver el dominio de identidad: {e}"
