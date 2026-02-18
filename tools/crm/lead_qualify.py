"""
Tool inteligente para calificar y avanzar Leads en el embudo de ventas.
"""
from app.auth import call_bitrix_method
import sys

async def lead_qualify(lead_id: int) -> str:
    """
    Evalúa y avanza automáticamente el Lead según la completitud de la información
    y el estado de asignación.
    
    Lógica:
    - NEW -> IN_PROCESS (IDENTIFICACIÓN): Si tiene Nombre + (Teléfono o Email).
    - IN_PROCESS -> UC_7AIMVU (ASIGNACIÓN): Si tiene un Responsable humano asignado.
    """
    sys.stderr.write(f"  🧠 Tool lead_qualify para ID: {lead_id}\n")

    try:
        # 1. Obtener datos actuales del Lead
        lead_res = await call_bitrix_method("crm.lead.get", {"id": lead_id})
        if not lead_res.get("result"):
            return f"Error: No se encontró el Lead {lead_id}."
        
        lead = lead_res["result"]
        current_status = lead.get("STATUS_ID")
        name = lead.get("NAME")
        phones = lead.get("PHONE", [])
        emails = lead.get("EMAIL", [])
        assigned_id = lead.get("ASSIGNED_BY_ID")
        
        has_phone = any(p.get("VALUE") for p in phones) if isinstance(phones, list) else False
        has_email = any(e.get("VALUE") for e in emails) if isinstance(emails, list) else False
        has_identity = bool(name and (has_phone or has_email))
        
        # 2. Evaluar transiciones
        new_status = None
        reason = ""

        # Transición: TRÁFICO (NEW) -> IDENTIFICACIÓN (IN_PROCESS)
        if current_status == "NEW" and has_identity:
            new_status = "IN_PROCESS"
            reason = "Información de identidad completada (Nombre + Contacto)."

        # Transición: IDENTIFICACIÓN (IN_PROCESS) -> ASIGNACIÓN (UC_7AIMVU)
        # Nota: Asumimos que si hay un asignado y ya pasamos la fase de identificación, 
        # alguien debe revisarlo. 
        # (Mejorar: Podríamos comparar con el ID del bot si lo tuviéramos fijo, 
        # pero por ahora avanzamos si hay identidad y estamos en proceso).
        elif current_status == "IN_PROCESS" and assigned_id:
            # Aquí podríamos verificar si el asignado ha cambiado del original
            new_status = "UC_7AIMVU"
            reason = "Lead listo para ser gestionado por un asesor."

        # 3. Aplicar cambio si aplica
        if new_status and new_status != current_status:
            sys.stderr.write(f"  ⬆️ Avanzando Lead a {new_status}...\n")
            update_res = await call_bitrix_method("crm.lead.update", {
                "id": lead_id,
                "fields": {"STATUS_ID": new_status}
            })
            
            if update_res.get("result"):
                return f"ÉXITO: Lead avanzado a etapa '{new_status}'. Motivo: {reason}"
            else:
                return f"Error al actualizar estado: {update_res.get('error_description')}"
        
        return f"INFO: El Lead {lead_id} se mantiene en etapa '{current_status}'. No cumple condiciones para avanzar aún."

    except Exception as e:
        sys.stderr.write(f"  ❌ Error en lead_qualify: {e}\n")
        return f"Error calificando lead: {e}"
