"""
Tool to get download link for a file.
"""
from app.auth import call_bitrix_method

def drive_file_download(file_id: int) -> str:
    """
    Usa esta tool para obtner el LINK de descarga de un archivo para enviárselo al usuario.
    
    Args:
        file_id: ID del archivo a descargar.
    """
    if not file_id:
        return "Error: Falta file_id"

    try:
        result = call_bitrix_method("disk.file.get", {
            "id": file_id
        })
        file_info = result.get("result", {})
        
        if not file_info:
             return f"No se encontró información para el archivo {file_id}."
             
        output = f"⬇️ Enlace de descarga para '{file_info.get('NAME')}':\n"
        output += f"{file_info.get('DOWNLOAD_URL')}\n"
        
        return output
        
    except Exception as e:
        return f"Error obteniendo link de descarga: {e}"
