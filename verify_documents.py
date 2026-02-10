"""
Verification script for Document Tools.
"""
import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.getcwd())
load_dotenv()

from tools.document.document_template_list import document_template_list
from tools.document.document_generate import document_generate
from tools.document.document_list import document_list
from tools.document.document_download import document_download

def verify():
    # Deal ID 10378 from previous catalog test
    deal_id = 10378
    entity_type_id = 2 # Deal

    print("📄 1. Listando Plantillas (Deal):")
    # Try generic list first if specific fails or just list all to see what we have
    templates_str = document_template_list() 
    print(templates_str)
    
    template_id = None
    if "ID: " in templates_str:
        try:
             # Parse first found template
             # Format: - ID: 10 | Nombre: ...
             line = templates_str.split("ID: ")[1]
             template_id = int(line.split(" |")[0])
             print(f"👉 Usaremos Template ID: {template_id}")
        except:
             print("⚠️ No pude extraer template ID.")
    else:
        # Fallback for simple list "- 46"
        for line in templates_str.split("\n"):
            line = line.strip()
            if line.startswith("- ") and "ID:" not in line:
                possible_id = line.replace("- ", "")
                if possible_id.isdigit():
                     template_id = int(possible_id)
                     print(f"👉 Usaremos Template ID (simple): {template_id}")
                     break

    if template_id:
        print(f"\n⚙️ 2. Generando documento para Deal {deal_id}...")
        gen_res = document_generate(template_id, deal_id, entity_type_id)
        print(gen_res)

        doc_id = None
        if "ID: " in gen_res:
            try:
                doc_id = int(gen_res.split("ID: ")[1].split("\n")[0])
                print(f"👉 Documento generado ID: {doc_id}")
            except:
                pass

        if doc_id:
            print(f"\n📂 3. Listando documentos del Deal {deal_id}:")
            print(document_list(deal_id, entity_type_id))
            
            print(f"\n⬇️ 4. Obteniendo link de descarga doc {doc_id}:")
            print(document_download(doc_id))

    print("\n✅ Verificación de documentos finalizada.")

if __name__ == "__main__":
    verify()
