"""
Tool inteligente para gestionar Leads: Busca duplicados, actualiza si existe, o crea uno nuevo.
"""
from app.auth import call_bitrix_method
import sys
import json

async def manage_lead(name: str = None, phone: str = None, email: str = None, 
                     title: str = None, chat_id: int = None, 
                     source_id: str = "WEB", comments: str = None) -> str:
    """
    Gestiona inteligentemente un Lead:
    1. Busca si ya existe un Lead o Contacto con ese teléfono o email.
    2. Si encuentra un LEAD existente: Lo actualiza con los nuevos datos.
    3. Si encuentra un CONTACTO existente: Crea un nuevo Lead vinculado a ese Contacto ("Cliente Recurrente").
    4. Si no encuentra nada: Crea un Lead nuevo desde cero.
    
    Args:
        name: Nombre del cliente (detectado o proporcionado).
        phone: Teléfono (importante para búsqueda).
        email: Email (importante para búsqueda).
        title: Título del lead (ej: "Interesado en Paquete X"). Si no se envía, se genera uno.
        chat_id: ID del chat para vincular la conversación.
        source_id: Origen del lead.
        comments: Nota o contexto inicial.
    """
    sys.stderr.write(f"  🧠 Tool manage_lead: name={name}, phone={phone}, chat_id={chat_id}\n")

    # 1. Validación mínima
    if not phone and not email:
        return "Error: Se requiere al menos un teléfono o email para gestionar el lead."

    try:
        # 2. Buscar Duplicados (Estrategia: crm.duplicate.findbycomm)
        existing_lead_id = None
        existing_contact_id = None
        
        clean_phone = phone.strip().replace(" ", "").replace("+", "") if phone else None
        search_values = [clean_phone] if clean_phone else [email.strip()]

        params = {
            "type": "PHONE" if phone else "EMAIL",
            "values": search_values
        }
        
        # A) Buscar en LEADS (Intento 1: Strict)
        try:
            lead_res = await call_bitrix_method("crm.duplicate.findbycomm", {**params, "entity_type": "LEAD"})
            # sys.stderr.write(f"DEBUG LEAD RES: {lead_res}\n")
            if lead_res.get("result"):
                leads_found = lead_res["result"]
                if isinstance(leads_found, list) and len(leads_found) > 0:
                    existing_lead_id = leads_found[0]
                    sys.stderr.write(f"  🔍 Lead existente encontrado (findbycomm): {existing_lead_id}\n")
        except Exception as e:
            sys.stderr.write(f"  ⚠️ Error buscando lead duplicado: {e}\n")

        if not existing_lead_id and phone:
             try:
                # Bitrix guarda telefonos en formato limpio a veces, o con formato. Buscamos exacto.
                filter_params = {"PHONE": phone.strip()} 
                list_res = await call_bitrix_method("crm.lead.list", {
                    "filter": filter_params, 
                    "select": ["ID", "TITLE", "PHONE"]
                })
                if list_res.get("result"):
                    leads_list = list_res["result"]
                    if leads_list:
                        existing_lead_id = leads_list[0]["ID"]
                        sys.stderr.write(f"  🔍 Lead existente encontrado (lead.list fallback): {existing_lead_id}\n")
             except Exception as e:
                 sys.stderr.write(f"  ⚠️ Error en fallback lead.list: {e}\n")

        # B) Buscar en CONTACTOS (si no encontramos Lead, o para vincular)
        try:
            contact_res = await call_bitrix_method("crm.duplicate.findbycomm", {**params, "entity_type": "CONTACT"})
            if contact_res.get("result"):
                contacts_found = contact_res["result"]
                if isinstance(contacts_found, list) and len(contacts_found) > 0:
                    existing_contact_id = contacts_found[0]
                    sys.stderr.write(f"  🔍 Contacto existente encontrado: {existing_contact_id}\n")
        except Exception as e:
            sys.stderr.write(f"  ⚠️ Error buscando contacto duplicado: {e}\n")

        sys.stderr.write(f"  📊 Resultados Búsqueda: Lead={existing_lead_id}, Contact={existing_contact_id}\n")

        # 3. Preparar campos de datos (comunes para crear o actualizar)
        fields = {}
        if title: fields["TITLE"] = title
        if name: fields["NAME"] = name
        if source_id: fields["SOURCE_ID"] = source_id
        if comments: fields["COMMENTS"] = comments
        
        # Campos multifield (Phone/Email)
        if phone: fields["PHONE"] = [{"VALUE": phone, "VALUE_TYPE": "WORK"}]
        if email: fields["EMAIL"] = [{"VALUE": email, "VALUE_TYPE": "WORK"}]

        action_taken = ""
        final_lead_id = None

        # CASO 1: Actualizar Lead Existente
        if existing_lead_id:
            sys.stderr.write(f"  🔄 Actualizando Lead {existing_lead_id}...\n")
            await call_bitrix_method("crm.lead.update", {"id": existing_lead_id, "fields": fields})
            final_lead_id = existing_lead_id
            action_taken = f"Lead {existing_lead_id} actualizado con nueva información."

        # CASO 2: Crear Nuevo Lead (Vinculado a Contacto si existe)
        else:
            # Si no hay title, generar uno genérico
            if not title:
                fields["TITLE"] = f"Lead de {name or 'Cliente'} ({phone or email})"
            
            fields["OPENED"] = "Y"
            
            # Si es cliente recurrente (Contacto existe), vinculamos
            if existing_contact_id:
                fields["CONTACT_ID"] = existing_contact_id
                action_taken = f"Nuevo Lead creado para cliente recurrente (Contacto {existing_contact_id})."
            else:
                action_taken = "Nuevo Lead creado (Prospecto nuevo)."

            sys.stderr.write(f"  🆕 Creando Lead nuevo...\n")
            
            # Si hay chat_id, usamos imopenlines.crm.lead.create para vincular visualmente
            if chat_id:
                try:
                   sys.stderr.write(f"  🔗 Usando imopenlines.crm.lead.create para vincular chat {chat_id}...\n")
                   create_res = await call_bitrix_method("imopenlines.crm.lead.create", {
                       "CHAT_ID": chat_id,
                       "FIELDS": fields
                   })
                except Exception as e:
                   sys.stderr.write(f"  ⚠️ Error en imopenlines.crm.lead.create: {e}. Reintentando con crm.lead.add...\n")
                   create_res = await call_bitrix_method("crm.lead.add", {"fields": fields})
            else:
                # Creación estándar sin chat
                create_res = await call_bitrix_method("crm.lead.add", {"fields": fields})
                
            final_lead_id = create_res.get("result")
            
            if not final_lead_id:
                return f"Error al crear lead: {create_res.get('error_description')}"

        # 4. Vincular Chat (Independientemente de si se creó o actualizó)
        if chat_id and final_lead_id:
            sys.stderr.write(f"  🔗 Vinculando chat {chat_id} al Lead {final_lead_id}...\n")
            
            # Intento de vinculación directa (im.chat.setEntity) - COMENTADO PORQUE DA 404
            # try:
            #     await call_bitrix_method("im.chat.setEntity", {
            #         "CHAT_ID": chat_id,
            #         "ENTITY_TYPE": "LEAD",
            #         "ENTITY_ID": final_lead_id
            #     })
            # except Exception as e:
            #      sys.stderr.write(f"  ⚠️ Warning vinculando chat: {e}\n")
            
            # Intento de registrar actividad en timeline (OpenLines message falló, usamos comentario standard)
            try:
                msg = f"[BOT] Gestión automática: {action_taken} (Chat ID: {chat_id})"
                # Usamos crm.timeline.comment.add que es más robusto y no requiere binding estricto de chat
                await call_bitrix_method("crm.timeline.comment.add", {
                    "fields": {
                        "ENTITY_ID": final_lead_id,
                        "ENTITY_TYPE": "lead",
                        "COMMENT": msg
                    }
                })
            except Exception as e:
                sys.stderr.write(f"  ⚠️ Warning en crm.timeline.comment.add: {e}\n")

        return f"GESTIÓN EXITOSA: {action_taken} (ID: {final_lead_id})"

    except Exception as e:
        sys.stderr.write(f"  ❌ Error en manage_lead: {e}\n")
        return f"Error gestionando lead: {e}"
