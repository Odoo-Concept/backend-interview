{
    "name": "Supermarket List",
    "description": "Módulo para gestionar una lista de supermercado",
    "icon": "/supermarket_list/static/description/supermarket_icon.png",
    "version": "18.0.1.0.1",
    "category": "Extra Tools",
    "summary": "Módulo integrador para el Proyecto",
    "author": "Erick Birbe <ebirbe@odooconcept.com>, Odoo Concept",
    "website": "https://odooconcept.com",
    "depends": [
        "base",
        "mail",
        "sale",
        "sale_management", 
    ],
    "data": [
        "security/ir.model.access.csv",

        "wizards/wizard_add_product_list_views.xml",
        
        "views/menu_views.xml",
        "views/supermarket_list_line_views.xml",
        "views/supermarket_list_views.xml",
        
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "OPL-1",
}
