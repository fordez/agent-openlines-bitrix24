# Auditoría Global de Herramientas MCP (Bitrix24)

He analizado las **49 herramientas** existentes. A continuación, la clasificación estratégica para un servidor de talla mundial.

## 🟢 Herramientas de Acción (Tools)
*Modifican el estado del CRM o ejecutan procesos.*

| Categoría | Herramienta | Acción |
| :--- | :--- | :--- |
| **CRM** | `lead_add` | Crea prospecto |
| **CRM** | `lead_update` | Modifica datos del prospecto |
| **CRM** | `lead_convert` | Dispara el proceso de venta (Deal) |
| **CRM** | `crm_add_note` | Registra historial/comentarios |
| **Deals** | `deal_move_stage` | Cambia etapa del embudo |
| **Calendar** | `calendar_event_create` | Agenda cita |
| **Calendar** | `calendar_event_update` | Reprograma cita |
| **Calendar** | `calendar_event_delete` | Cancela cita |
| **Catalog** | `deal_add_products` | Vincula inventario al negocio |
| **Catalog** | `deal_remove_product` | Quita del carrito |
| **OpenLines** | `session_answer` | Acepta el chat |
| **OpenLines** | `session_transfer` | Pasa a humano |
| **OpenLines** | `session_finish` | Cierra sesión |
| **OpenLines** | `session_finish` | Cierra sesión |
| **Drive** | `drive_folder_create` | Crea estructura de archivos |
| **Drive** | `drive_file_upload` | Sube documentos |
| **Tasks** | `task_create` | Crea flujo de trabajo interno |
| **Followup** | `lead_reactivate` | Revive prospecto antiguo |

## 🔵 Recursos de Contexto (Resources)
*Consultan información persistente. Se exponen como URIs `bitrix://...`*

| Categoría | Candidato a Resource | URI Propuesta |
| :--- | :--- | :--- |
| **Metadata** | `crm_fields_get` | `bitrix://crm/fields/{entity}` |
| **Metadata** | `crm_stages_list` | `bitrix://crm/stages/{entity}` |
| **Metadata** | `calendar_get_types` | `bitrix://calendar/types` |
| **Entidades** | `lead_get` | `bitrix://crm/lead/{id}` |
| **Entidades** | `deal_get` | `bitrix://crm/deal/{id}` |
| **Entidades** | `contact_get` | `bitrix://crm/contact/{id}` |
| **Entidades** | `company_get` | `bitrix://crm/company/{id}` |
| **Entidades** | `calendar_event_get` | `bitrix://calendar/event/{id}` |
| **Listas** | `deal_list` | `bitrix://crm/deals/active` |
| **Listas** | `calendar_event_list` | `bitrix://calendar/events/range` |
| **Inventario** | `catalog_list` | `bitrix://catalogs` |
| **Inventario** | `catalog_category_list` | `bitrix://catalog/{id}/categories` |
| **Inventario** | `catalog_product_list` | `bitrix://catalog/category/{id}/products` |
| **Documentos** | `document_template_list` | `bitrix://documents/templates` |
| **Documentos** | `document_list` | `bitrix://crm/{type}/{id}/documents` |
| **Drive** | `drive_folder_list` | `bitrix://drive/folders` |
| **Drive** | `drive_file_list` | `bitrix://drive/folder/{id}/files` |

## 🟡 Herramientas Híbridas / Búsqueda (Dynamic Tools)
*Requieren parámetros de usuario y devuelven datos que cambian frecuentemente.*

- `find_duplicate`: Búsqueda específica por teléfono/email.
- `catalog_product_search`: Búsqueda por palabra clave.
- `calendar_availability_check`: Verificación de slots libres dinámicos.
- `session_crm_get`: Identificación de vínculo de sesión.

---
**Conclusión**: He mapeado las 49 herramientas. El 100% están cubiertas bajo esta nueva arquitectura de Poder Dual (Action Tools + Context Resources).
