"""
Herramienta para crear un Lead en Bitrix24.
Usa el método: crm.lead.add
"""
from app.auth import call_bitrix_method
import json


def lead_add(title: str, name: str = None, last_name: str = None, phone: str = None, email: str = None,
             source_id: str = "WEB", comments: str = None, assigned_by_id: str = None) -> str:
    """
    Usa esta tool para CREAR un nuevo Lead cuando identifiques un cliente potencial nuevo que no existe.
    
    Args:
        title: Título del Lead (ej: "Interesado en Paquete Madrid").
        name, last_name: Nombre del cliente.
        phone, email: Datos de contacto.
        source_id: Fuente del lead (ej: 'WEB', 'CALL', 'WEBFORM', 'CALLBACK').
        comments: Comentarios o notas adicionales.
        assigned_by_id: ID del responsable asignado.

    Returns:
        str: ID del Lead creado o mensaje de error.
    """
    if not title:
        return "Error: title es requerido para crear un Lead."

    fields = {"TITLE": title, "OPENED": "Y"}

    if name:
        fields["NAME"] = name
    if last_name:
        fields["LAST_NAME"] = last_name
    if phone:
        fields["PHONE"] = [{"VALUE": phone, "VALUE_TYPE": "WORK"}]
    if email:
        fields["EMAIL"] = [{"VALUE": email, "VALUE_TYPE": "WORK"}]
    if source_id:
        fields["SOURCE_ID"] = source_id
    if comments:
        fields["COMMENTS"] = comments
    if assigned_by_id:
        fields["ASSIGNED_BY_ID"] = assigned_by_id

    try:
        result = call_bitrix_method("crm.lead.add", {"fields": fields})
        lead_id = result.get("result")
        if lead_id:
            return f"Lead creado exitosamente con ID: {lead_id}."
        else:
            error = result.get("error_description", result)
            return f"Error creando lead: {error}"
    except Exception as e:
        return f"Error creando lead: {e}"
