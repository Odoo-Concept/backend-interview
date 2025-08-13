{
    "name": "Grocery list",
    "version": "18.0.1.0.1",
    "category": "Extra Tools",
    "summary": "Gestionar listas de compras del supermercado",
    "author": "Agustín Lorca <aguslorca.12@gmail.com>, Odoo Concept",
    "website": "https://odooconcept.com",
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/grocery_list_item_views.xml",
        "views/grocery_list_views.xml",
        "views/menu_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "OPL-1",
}
