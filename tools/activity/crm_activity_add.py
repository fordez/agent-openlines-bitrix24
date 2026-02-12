"""
Tool to add a CRM activity (Call, Meeting, etc.) in Bitrix24.
"""
from app.auth import call_bitrix_method
import sys

async def crm_activity_add(entity_id: int, entity_type: str, subject: str, 
                         type_id: int = 2, start_time: str = None, 
                         end_time: str = None, description: str = "") -> str:
    """
    Agrega una ACTIVIDAD al CRM (Llamada, Reunión, Email).
    Diferente a una Tarea: Las actividades son seguimientos ligeros con fecha.
    
    Args:
        entity_id: ID del Lead o Deal.
        entity_type: "LEAD" o "DEAL".
        subject: Título de la actividad (ej: "Llamada para revisar itinerario").
        type_id: 1=Meeting, 2=Call, 3=Email, 4=Task (liger), 5=IM. Por defecto 2 (Call).
        start_time: Fecha/hora de inicio (ISO 8601).
        end_time: Fecha/hora de fin (ISO 8601).
        description: Detalles adicionales.
    """
    if not entity_id or not entity_type or not subject:
        return "Error: Faltan argumentos obligatorios (entity_id, entity_type, subject)."

    etype_id = 1 if entity_type.upper() == "LEAD" else 2
    
    fields = {
        "OWNER_ID": entity_id,
        "OWNER_TYPE_ID": etype_id,
        "TYPE_ID": type_id,
        "SUBJECT": subject,
        "DESCRIPTION": description,
        "COMPLETED": "N"
    }
    
    if start_time:
        fields["START_TIME"] = start_time
    if end_time:
        fields["END_TIME"] = end_time

    try:
        result = await call_bitrix_method("crm.activity.add", {"fields": fields})
        activity_id = result.get("result")
        if not activity_id:
            return f"Error al crear actividad: {result.get('error_description', 'Respuesta vacía')}"
            
        return f"Actividad creada exitosamente:\n- ID: {activity_id}\n- Asunto: {subject}\n- Tipo: {type_id}"
        
    except Exception as e:
        return f"Error técnico creando actividad: {e}"
