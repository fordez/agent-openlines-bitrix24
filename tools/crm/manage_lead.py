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

            # Metadata para vincular chat a la ficha
            chat_metadata = {}
            if chat_id:
                try:
                    # Obtener detalles del diálogo para extraer USER_CODE, LINE_ID y SESSION_ID
                    dialog_res = await call_bitrix_method("imopenlines.dialog.get", {"CHAT_ID": chat_id})
                    if dialog_res.get("result"):
                        d = dialog_res["result"]
                        # imol|workflow_whatsapp|24|573158273960|1068
                        user_code = d.get("entity_link", {}).get("id", "") or d.get("entity_id", "")
                        
                        # Extraer Session ID de entity_data_1 (sexto parámetro)
                        data_1 = d.get("entity_data_1", "")
                        session_id = None
                        if data_1 and "|" in data_1:
                            parts = data_1.split("|")
                            if len(parts) >= 6:
                                session_id = parts[5]
                        
                        chat_metadata = {
                            "USER_CODE": user_code,
                            "LINE_ID": d.get("entity_id", "").split("|")[1] if "|" in d.get("entity_id", "") else "0",
                            "SESSION_ID": session_id
                        }
                        
                        if user_code:
                            fields["IM"] = [{"VALUE": f"imol|{user_code}", "VALUE_TYPE": "IMOL"}]
                            sys.stderr.write(f"  🔗 Preparado vínculo IMOL: {user_code}\n")
                except Exception as e:
                    sys.stderr.write(f"  ⚠️ Error obteniendo metadata del chat: {e}\n")

            sys.stderr.write(f"  🆕 Creando Lead nuevo mediante crm.lead.add...\n")
            create_res = await call_bitrix_method("crm.lead.add", {"fields": fields})
            final_lead_id = create_res.get("result")
            
            if not final_lead_id:
                return f"Error al crear lead: {create_res.get('error_description', 'Error desconocido')}"
            
            sys.stderr.write(f"  ✅ Lead nuevo ID: {final_lead_id}\n")

        # 4. Vincular Chat (Independientemente de si se creó o actualizó)
        if chat_id and final_lead_id:
            sys.stderr.write(f"  🔗 Vinculando chat {chat_id} al Lead {final_lead_id}...\n")
            
            # 1. Crear ACTIVIDAD DE SESIÓN (Fuerza el vínculo visual en el Contact Center)
            try:
                # Si no tenemos metadata (porque fue un update), intentamos obtenerla ahora
                if not locals().get("chat_metadata"):
                    dialog_res = await call_bitrix_method("imopenlines.dialog.get", {"CHAT_ID": chat_id})
                    if dialog_res.get("result"):
                        d = dialog_res["result"]
                        user_code = d.get("entity_link", {}).get("id", "") or d.get("entity_id", "")
                        data_1 = d.get("entity_data_1", "")
                        session_id = data_1.split("|")[5] if "|" in data_1 and len(data_1.split("|")) >= 6 else None
                        chat_metadata = {
                            "USER_CODE": user_code,
                            "LINE_ID": d.get("entity_id", "").split("|")[1] if "|" in d.get("entity_id", "") else "0",
                            "SESSION_ID": session_id
                        }

                if chat_metadata.get("SESSION_ID"):
                    await call_bitrix_method("crm.activity.add", {
                        "fields": {
                            "OWNER_ID": final_lead_id,
                            "OWNER_TYPE_ID": 1, # Lead
                            "TYPE_ID": 6,       # IM
                            "PROVIDER_ID": "IMOPENLINES_SESSION",
                            "PROVIDER_TYPE_ID": chat_metadata["LINE_ID"],
                            "ASSOCIATED_ENTITY_ID": chat_metadata["SESSION_ID"],
                            "SUBJECT": f"Sesión de Chat (Canal Abierto)",
                            "COMPLETED": "Y",
                            "DIRECTION": 1,
                            "ORIGIN_ID": f"IMOL_{chat_metadata['SESSION_ID']}",
                            "PROVIDER_PARAMS": {"USER_CODE": chat_metadata["USER_CODE"]}
                        }
                    })
                    sys.stderr.write(f"  ⛓️ Actividad de sesión vinculada.\n")
            except Exception as e:
                sys.stderr.write(f"  ⚠️ Error creando actividad de vínculo: {e}\n")

            # 2. Registrar NOTA en el timeline (Backup visual)
            try:
                msg = f"[BOT] Gestión automática: {action_taken} (Chat ID: {chat_id})"
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
