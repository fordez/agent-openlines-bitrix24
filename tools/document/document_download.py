"""
Tool to get download link for a document.
"""
from app.auth import call_bitrix_method

async def document_download(document_id: int) -> str:
    """
    Usa esta tool para obtener el LINK de descarga de un documento generado (PDF/Word).
    
    Args:
        document_id: ID del documento generado.
    """
    if not document_id:
        return "Error: Falta document_id"

    try:
        result = await call_bitrix_method("crm.documentgenerator.document.get", {"id": document_id})
        doc = result.get("result", {})
        
        if not doc:
            return f"No se encontró documento con ID {document_id}."
            
        output = f"⬇️ Enlaces para documento {document_id} ({doc.get('title')}):\n"
        output += f"- PDF: {doc.get('pdfUrl')}\n"
        output += f"- Word/Doc: {doc.get('downloadUrl')}\n"
        output += f"- Imagen: {doc.get('imageUrl')}\n"
        
        return output
        
    except Exception as e:
        return f"Error obteniendo descarga: {e}"
