"""
Tool to generate documents from templates.
"""
from app.auth import call_bitrix_method

def document_generate(template_id: int, entity_id: int, entity_type_id: int = 2) -> str:
    """
    Usa esta tool para GENERAR un documento (ej: PDF de Cotización) usando una plantilla.
    
    Args:
        template_id: ID de la plantilla a usar.
        entity_id: ID del Deal o Lead con los datos.
        entity_type_id: 1=Lead, 2=Deal.
    """
    if not template_id or not entity_id or not entity_type_id:
        return "Error: Faltan argumentos (template_id, entity_id, entity_type_id)"

    try:
        # values={} can be passed to override fields, but usually we rely on CRM data
        result = call_bitrix_method("crm.documentgenerator.document.add", {
            "templateId": template_id,
            "entityTypeId": entity_type_id,
            "entityId": entity_id
        })
        
        doc = result.get("result", {})
        if not doc:
            return "No se pudo generar el documento (respuesta vacía)."
            
        output = f"Documento generado exitosamente.\n"
        output += f"- ID: {doc.get('id')}\n"
        output += f"- Título: {doc.get('title')}\n"
        output += f"- URL Detalle: {doc.get('detailUrl')}\n"
        output += f"- URL Descarga: {doc.get('downloadUrl')}\n"
        output += f"- URL PDF: {doc.get('pdfUrl')}\n"
        
        return output
        
    except Exception as e:
        return f"Error generando documento: {e}"
