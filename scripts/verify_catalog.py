"""
Verification script for Catalog Tools.
"""
import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from tools.catalog.catalog_list import catalog_list
from tools.catalog.catalog_category_list import catalog_category_list
from tools.catalog.catalog_product_list import catalog_product_list
from tools.catalog.catalog_product_get import catalog_product_get
from tools.catalog.catalog_product_search import catalog_product_search
from tools.catalog.deal_add_products import deal_add_products
from tools.catalog.deal_update_products import deal_update_products
from tools.catalog.deal_remove_product import deal_remove_product
from tools.deal.deal_list import deal_list

def verify():
    print("🛒 1. Listando Catálogos:")
    catalogs_out = catalog_list()
    print(catalogs_out)
    
    # Try to extract a catalog ID. Usually ID 21 is default/CRM one in older Bitrix, or we parse.
    # For now let's just assume we list categories of the first one found or a hardcoded one if output is string.
    # We will search for a product directly to get IDs since catalog might be complex to parse from string in this script without regex.
    
    print("\n🔍 2. Buscando productos (keyword 'a')...") # 'a' finds almost anything
    search_res = catalog_product_search("a")
    print(search_res)
    
    product_id = None
    if "ID: " in search_res:
         # Rough parse first ID
         try:
             product_id = int(search_res.split("ID: ")[1].split(" |")[0])
             print(f"👉 Product ID encontrado: {product_id}")
         except:
             print("⚠️ No pude parsear product ID del search result.")

    if product_id:
        print(f"\n📄 3. Detalles de producto {product_id}:")
        print(catalog_product_get(product_id))

    # Get a deal to test adding products
    print("\n🤝 4. Buscando un Deal para prueba...")
    deals_out = deal_list({}, ["ID", "TITLE"])
    deal_id = None
    if "ID: " in deals_out:
        try:
            deal_id = deals_out.split("ID: ")[1].split(" |")[0]
            print(f"👉 Deal ID encontrado: {deal_id}")
        except:
             pass
    
    if deal_id and product_id:
        print(f"\n➕ 5. Agregando producto {product_id} al Deal {deal_id}...")
        add_res = deal_add_products(deal_id, [{"product_id": product_id, "price": 100, "quantity": 1}])
        print(add_res)
        
        row_id = None
        if "Row ID: " in add_res:
            try:
                row_id = int(add_res.split("Row ID: ")[1].split(")")[0])
                print(f"👉 Row ID creado: {row_id}")
            except:
                pass
        
        if row_id:
            print(f"\n✏️ 6. Actualizando fila {row_id} (Quantity: 5)...")
            print(deal_update_products(row_id, {"quantity": 5}))

            print(f"\n🗑️ 7. Eliminando fila {row_id}...")
            print(deal_remove_product(row_id))

    print("\n✅ Verificación de catálogo finalizada.")

if __name__ == "__main__":
    verify()
