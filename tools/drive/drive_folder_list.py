"""
Tool to list folders in Bitrix24 Drive.
"""
from app.auth import call_bitrix_method

async def drive_folder_list(folder_id: int = None) -> str:
    """
    Usa esta tool para explorar carpetas en el Drive si el usuario pide ver archivos o buscar donde guardar algo.
    Si no das folder_id, muestra la raíz.

    Args:
        folder_id: (Opcional) ID de la carpeta a listar.
    """
    if not folder_id:
        try:
            # Get default storage
            storage_res = await call_bitrix_method("disk.storage.getlist", {})
            storages = storage_res.get("result", [])
            if storages:
                # Usually first storage is Company Drive or User Drive depending on scope
                # We can also look for NAME='Company Drive'
                root_id = storages[0].get("ROOT_OBJECT_ID")
                folder_id = root_id
            else:
                return "No se encontraron almacenamientos en el Drive."
        except Exception as e:
            return f"Error buscando almacenamiento raíz: {e}"

    try:
        result = await call_bitrix_method("disk.folder.getchildren", {
            "id": folder_id,
            "filter": {"TYPE": "folder"} 
        })
        children = result.get("result", [])
        
        if not children:
            return f"No se encontraron carpetas en ID {folder_id}."
            
        output = f"Carpetas en {folder_id}:\n"
        for c in children:
            output += f"- ID: {c.get('ID')} | Nombre: {c.get('NAME')}\n"
            
        return output
        
    except Exception as e:
        return f"Error listando carpetas: {e}"
