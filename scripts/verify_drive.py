"""
Verification script for Drive Tools.
"""
import sys
import os
import base64
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from tools.drive.drive_folder_list import drive_folder_list
from tools.drive.drive_folder_create import drive_folder_create
from tools.drive.drive_file_upload import drive_file_upload
from tools.drive.drive_file_list import drive_file_list
from tools.drive.drive_file_download import drive_file_download

def verify():
    print("📂 1. Buscando carpeta raíz y listando:")
    # List root (None -> auto find root)
    root_list = drive_folder_list()
    # print(root_list) # Too verbose usually

    # We need a folder ID to create subfolder.
    # drive_folder_list output format: "- ID: 10 | Nombre: ..."
    root_id = None
    if "ID: " in root_list:
        # Extract first ID (which might be a child, or we assume storage root is not returned but children)
        # Wait, drive_folder_list returns children of root.
        # But we need the ID of the ROOT explicitly or one of the children to be parent.
        # Ideally verify script should get the storage root ID differently or parse from a known logic?
        # drive_folder_list uses storage.getlist to find root if None passed.
        # To be safe, let's just use the first folder found as parent, OR modify drive_folder_list to return root_id too?
        # No, let's just rely on parsing the output which gives children. If I want to create folder in "Company Drive", I need its ID, which drive_folder_list uses internally as default.
        # I'll create a folder in one of the existing children for test safety, or I'll implement a 'get_root_id' function?
        # Actually, let's parse the first child ID and create inside it. That's safer than root which might be read-only if permissions vary.
        try:
             first_line = root_list.split("\n")[1] # Skip header
             if "ID: " in first_line:
                 root_id = int(first_line.split("ID: ")[1].split(" |")[0])
                 print(f"👉 Usaremos Carpeta ID (existente): {root_id}")
        except:
             pass

    if root_id:
        new_folder_name = "Folder Prueba Bot"
        print(f"\n📁 2. Creando subcarpeta '{new_folder_name}' en ID {root_id}...")
        create_res = drive_folder_create(root_id, new_folder_name)
        print(create_res)
        
        new_folder_id = None
        if "ID: " in create_res:
             try:
                 new_folder_id = int(create_res.split("ID: ")[1].split("\n")[0])
                 print(f"👉 Nueva Carpeta ID: {new_folder_id}")
             except:
                 pass
        
        if new_folder_id:
            print(f"\n⬆️ 3. Subiendo archivo a carpeta {new_folder_id}...")
            content = "Hola desde el Bot!"
            content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            upload_res = drive_file_upload(new_folder_id, "test_bot_file.txt", content_b64)
            print(upload_res)
            
            file_id = None
            if "ID: " in upload_res:
                try:
                    file_id = int(upload_res.split("ID: ")[1].split("\n")[0])
                    print(f"👉 Archivo subido ID: {file_id}")
                except:
                    pass

            if file_id:
                print(f"\n📄 4. Listando archivos en carpeta {new_folder_id}:")
                print(drive_file_list(new_folder_id))
                
                print(f"\n⬇️ 5. Obteniendo link de descarga archivo {file_id}:")
                print(drive_file_download(file_id))

    print("\n✅ Verificación de Drive finalizada.")

if __name__ == "__main__":
    verify()
