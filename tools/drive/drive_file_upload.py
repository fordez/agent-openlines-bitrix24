"""
Tool to upload files to Bitrix24 Drive.
"""
from app.auth import call_bitrix_method

def drive_file_upload(folder_id: int, name: str, content_base64: str) -> str:
    """
    Usa esta tool para SUBIR un archivo generado (PDF, cotización) a una carpeta del Drive.
    
    Args:
        folder_id: ID de la carpeta destino.
        name: Nombre del archivo con extensión (ej: "contrato.pdf").
        content_base64: Contenido del archivo en base64.
    """
    if not folder_id or not name or not content_base64:
        return "Error: Faltan argumentos (folder_id, name, content_base64)"

    try:
        result = call_bitrix_method("disk.folder.uploadfile", {
            "id": folder_id,
            "data": {"NAME": name},
            "fileContent": content_base64
        })
        
        file_info = result.get("result", {})
        if not file_info:
             return "Error al subir archivo (respuesta vacía)."
             
        return f"Archivo subido exitosamente:\n- ID: {file_info.get('ID')}\n- Nombre: {file_info.get('NAME')}\n- Link Detalle: {file_info.get('DETAIL_URL')}"
        
    except Exception as e:
        return f"Error subiendo archivo: {e}"
