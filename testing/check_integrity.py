"""
Script de verificación de integridad del código.
Intenta importar todos los módulos para detectar errores de sintaxis o imports rotos.
"""
import sys
import os
import importlib

# Add project root to path
sys.path.append(os.getcwd())

modules_to_check = [
    "app.gemini_agent",
    "app.auth",
    "app.bitrix",
    "tools.crm.resolve_identity",
    "tools.crm.enrich_identity",
    "tools.crm.qualify_lead",
    "tools.deal.get_or_create_deal",
    "tools.deal.update_deal_stage",
    "tools.deal.update_deal_fields",
    "tools.deal.add_deal_note",
    "tools.deal.close_deal",
    "tools.calendar.get_availability",
    "tools.calendar.create_event",
    "tools.calendar.update_event",
    "tools.calendar.reschedule_event",
    "tools.calendar.cancel_event",
    "tools.calendar.get_event",
    "tools.calendar.schedule_meeting",
    "tools.activity.create_activity",
    "tools.activity.update_activity",
    "tools.activity.complete_activity",
    "tools.activity.schedule_followup",
    "tools.automation.detect_sales_stage",
    "tools.automation.predict_close_probability",
    "tools.automation.handle_objection",
    "tools.automation.reactivate_lead",
]

print("--- Iniciando verificación de imports ---\n")
errors = []

for module in modules_to_check:
    try:
        importlib.import_module(module)
        print(f"✅ {module} importado correctamente.")
    except Exception as e:
        print(f"❌ Error en {module}: {e}")
        errors.append(f"{module}: {e}")

print("\n--- Resultado ---")
if errors:
    print(f"Se encontraron {len(errors)} errores:")
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)
else:
    print("Todos los módulos son válidos.")
    sys.exit(0)
