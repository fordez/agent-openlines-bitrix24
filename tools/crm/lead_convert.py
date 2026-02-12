"""
Herramienta para convertir un Lead en Contacto + Deal en Bitrix24.
Usa crm.lead.update y luego crea Contacto/Deal manualmente.
"""
from app.auth import call_bitrix_method
import json
import sys

async def lead_convert(lead_id: int, deal_category_id: int = 0, chat_id: int = None, create_deal: bool = True, create_contact: bool = True, create_company: bool = False) -> str:
    """
    CONVIERTE un Lead en Deal, Contacto y/o Empresa según los flags proporcionados.
    Permite todas las combinaciones posibles de conversión (ej: Solo Contacto, Deal + Contacto, etc).
    """
    if not lead_id:
        return "Error: lead_id es requerido."

    if not (create_deal or create_contact or create_company):
         return "Error: Debes seleccionar al menos una entidad para crear (Deal, Contacto o Empresa)."

    sys.stderr.write(f"  🚀 Tool lead_convert: lead_id={lead_id}, deal={create_deal}, contact={create_contact}, company={create_company}\n")

    try:
        # 1. Obtener datos del Lead
        lead_data = await call_bitrix_method("crm.lead.get", {"id": lead_id})
        lead = lead_data.get("result")
        if not lead:
            return f"Error: no se encontró el Lead {lead_id}."

        contact_id = None
        company_id = None
        deal_id = None
        entities_created = []

        # 2. Crear Contacto
        if create_contact:
            contact_fields = {
                "NAME": lead.get("NAME", ""),
                "LAST_NAME": lead.get("LAST_NAME", ""),
                "OPENED": "Y",
                "SOURCE_ID": lead.get("SOURCE_ID", ""),
            }
            if lead.get("PHONE"): contact_fields["PHONE"] = lead["PHONE"]
            if lead.get("EMAIL"): contact_fields["EMAIL"] = lead["EMAIL"]
            if lead.get("ASSIGNED_BY_ID"): contact_fields["ASSIGNED_BY_ID"] = lead["ASSIGNED_BY_ID"]

            contact_result = await call_bitrix_method("crm.contact.add", {"fields": contact_fields})
            contact_id = contact_result.get("result")
            if contact_id:
                entities_created.append(f"CONTACTO:{contact_id}")

        # 3. Crear Empresa (Opcional - Caso B2B)
        if create_company:
            # Si el lead tiene COMPANY_TITLE usamos ese, si no usamos el apellido como nombre de empresa
            company_title = lead.get("COMPANY_TITLE") or f"Empresa de {lead.get('LAST_NAME', 'Cliente')}"
            company_fields = {
                "TITLE": company_title,
                "OPENED": "Y"
            }
            if lead.get("PHONE"): company_fields["PHONE"] = lead["PHONE"]
            if lead.get("EMAIL"): company_fields["EMAIL"] = lead["EMAIL"]
            
            
            company_result = await call_bitrix_method("crm.company.add", {"fields": company_fields})
            company_id = company_result.get("result")
            if company_id:
                entities_created.append(f"EMPRESA:{company_id}")
                # Vincular contacto a la empresa (si se creó contacto)
                if contact_id:
                    await call_bitrix_method("crm.contact.update", {
                        "id": contact_id,
                        "fields": {"COMPANY_ID": company_id}
                    })

        # 4. Crear Deal (Negocio)
        if create_deal:
            deal_title = lead.get("TITLE") or f"Negocio: {lead.get('NAME')} {lead.get('LAST_NAME')}"
            deal_fields = {
                "TITLE": deal_title,
                "OPENED": "Y",
                "CATEGORY_ID": deal_category_id,
                "OPPORTUNITY": lead.get("OPPORTUNITY", 0),
                "CURRENCY_ID": lead.get("CURRENCY_ID", "USD")
            }
            if contact_id: deal_fields["CONTACT_ID"] = contact_id
            if company_id: deal_fields["COMPANY_ID"] = company_id
            if lead.get("ASSIGNED_BY_ID"): deal_fields["ASSIGNED_BY_ID"] = lead["ASSIGNED_BY_ID"]

            deal_result = await call_bitrix_method("crm.deal.add", {"fields": deal_fields})
            deal_id = deal_result.get("result")
            
            if deal_id:
                entities_created.append(f"DEAL:{deal_id}")
            else:
                return f"Error al crear Deal: {deal_result.get('error_description')} (Entities: {entities_created})"

        # 5. La vinculación del chat en Bitrix24 Open Channels se hereda o se gestiona por el sistema.
        # 5. La vinculación de chat se gestiona de forma nativa por Bitrix24 en Open Channels.
        if chat_id:
            sys.stderr.write(f"  ℹ️ Conversión para chat {chat_id}. Bitrix24 gestionará el vínculo automáticamente.\n")

        # 6. Finalizar Lead (Marcar como convertido)
        await call_bitrix_method("crm.lead.update", {
            "id": lead_id,
            "fields": {"STATUS_ID": "CONVERTED"}
        })

        return f"CONVERSIÓN EXITOSA. Entidades creadas: {', '.join(entities_created)}. El Lead {lead_id} ha sido cerrado."

    except Exception as e:
        sys.stderr.write(f"  ❌ Error en lead_convert: {e}\n")
        return f"Error convirtiendo lead: {e}"
