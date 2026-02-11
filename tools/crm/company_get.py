"""
Tool to get full company details.
"""
from app.auth import call_bitrix_method

async def company_get(company_id: int) -> str:
    """
    Obtener toda la información de una Empresa por su ID.
    
    Args:
        company_id: ID de la Empresa.
    """
    if not company_id:
        return "Error: Falta company_id"

    try:
        result = await call_bitrix_method("crm.company.get", {"id": company_id})
        company = result.get("result")
        
        if not company:
            return f"No se encontró la Empresa {company_id}."
            
        output = f"Detalles de la Empresa {company_id}:\n"
        for k, v in company.items():
            if v and not isinstance(v, (list, dict)):
                output += f"- {k}: {v}\n"
            elif v:
                output += f"- {k}: {str(v)}\n"
                
        return output
        
    except Exception as e:
        return f"Error obteniendo empresa: {e}"
