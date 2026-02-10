"""
Tool to search deals by contact, stage, responsible, or custom filters.
"""
from app.auth import call_bitrix_method
import json

def deal_list(filter_status: str = None, limit: int = 10) -> str:
    """
    Usa esta tool para LISTAR Deals activos, filtrados por etapa si es necesario.
    Útil para ver qué negocios tiene abiertos un cliente.
    
    Args:
        filter_status: (Opcional) ID de la etapa (STAGE_ID).
        limit: Cantidad de resultados.
    """
    if filter_params is None:
        filter_params = {}
        
    if isinstance(filter_params, str):
        try:
            filter_params = json.loads(filter_params)
        except:
            return "Error: filter_params debe ser un diccionario válido o JSON string."
            
    # Default select fields if not provided
    if not select:
        select = ["ID", "TITLE", "STAGE_ID", "OPPORTUNITY", "CURRENCY_ID", "CONTACT_ID", "ASSIGNED_BY_ID", "CLOSED", "DATE_CREATE"]

    try:
        result = call_bitrix_method("crm.deal.list", {
            "filter": filter_params,
            "select": select,
            "order": {"DATE_CREATE": "DESC"},
            "limit": 10  # Limitar a 10 para no saturar al agente
        })
        
        deals = result.get("result", [])
        
        if not deals:
            return "No se encontraron deals con los filtros proporcionados."
            
        output = "Deals encontrados:\n"
        for d in deals:
            output += (
                f"- ID: {d.get('ID')} | Título: {d.get('TITLE')} | Etapa: {d.get('STAGE_ID')} | "
                f"Monto: {d.get('OPPORTUNITY')} {d.get('CURRENCY_ID')} | Cerrado: {d.get('CLOSED')}\n"
            )
            
        return output

    except Exception as e:
        return f"Error buscando deals: {e}"
