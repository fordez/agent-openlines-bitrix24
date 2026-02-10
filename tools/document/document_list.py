"""
Tool to list generated documents for an entity.
"""
from app.auth import call_bitrix_method

def document_list(entity_id: int, entity_type_id: int = 2) -> str:
    """
    Usa esta tool para buscar documentos YA generados para un Deal/Lead específico.
    
    Args:
        entity_id: ID del Deal o Lead.
        entity_type_id: 1=Lead, 2=Deal.
    """
    if not entity_id or not entity_type_id:
        return "Error: Faltan argumentos"

    try:
        result = call_bitrix_method("crm.documentgenerator.document.list", {
            "filter": {
                "entityId": entity_id,
                "entityTypeId": entity_type_id
            }
        })
        
        docs = result.get("result", [])
        if not docs:
            return "No hay documentos generados para esta entidad."
            
        output = "Documentos Generados:\n"
        for d in docs:
            output += f"- ID: {d.get('id')} | {d.get('title')} | PDF: {d.get('pdfUrl')}\n"
            
        return output
        
    except Exception as e:
        return f"Error listando documentos: {e}"
