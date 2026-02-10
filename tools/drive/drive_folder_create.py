"""
Tool to create a folder in Bitrix24 Drive.
"""
from app.auth import call_bitrix_method

async def drive_folder_create(parent_folder_id: int, name: str) -> str:
    """
    Usa esta tool para crear una carpeta NUEVA, por ejemplo para organizar documentos de un Cliente o Deal.
    
    Args:
        parent_folder_id: ID de la carpeta donde se creará.
        name: Nombre de la nueva carpeta (ej: "Cliente Juan Perez").
    """
    if not parent_folder_id or not name:
        return "Error: Faltan argumentos (parent_folder_id, name)"

    try:
        result = await call_bitrix_method("disk.folder.addsubfolder", {
            "id": parent_folder_id,
            "data": {"NAME": name}
        })
        
        folder = result.get("result", {})
        if not folder:
             return "Error al crear carpeta (respuesta vacía)."
             
        return f"Carpeta creada exitosamente:\n- ID: {folder.get('ID')}\n- Nombre: {folder.get('NAME')}"
        
    except Exception as e:
        return f"Error creando carpeta: {e}"
