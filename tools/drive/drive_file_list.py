"""
Tool to list files in a folder.
"""
from app.auth import call_bitrix_method

def drive_file_list(folder_id: int) -> str:
    """
    Usa esta tool para ver qué ARCHIVOS hay dentro de una carpeta específica.
    Útil para revisar si ya existe un documento.

    Args:
        folder_id: ID de la carpeta.
    """
    if not folder_id:
        return "Error: Falta folder_id"

    try:
        result = call_bitrix_method("disk.folder.getchildren", {
            "id": folder_id,
            "filter": {"TYPE": "file"}
        })
        children = result.get("result", [])
        
        # Filter again in python just in case check 'TYPE' field
        files = [c for c in children if c.get('TYPE') == 'file']
        
        if not files:
            return f"No se encontraron archivos en la carpeta {folder_id}."
            
        output = f"Archivos en carpeta {folder_id}:\n"
        for f in files:
            output += f"- ID: {f.get('ID')} | Nombre: {f.get('NAME')} | Tamaño: {f.get('SIZE')} bytes\n"
            
        return output
        
    except Exception as e:
        return f"Error listando archivos: {e}"
