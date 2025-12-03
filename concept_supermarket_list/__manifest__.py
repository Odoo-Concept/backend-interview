{
    "name": "SuperMarket List",
    "version": "18.0.1.0.1",
    "category": "Extra Tools",
    "summary": "",
    "author": ""
    "Erick Birbe <ebirbe@odooconcept.com>, Odoo Concept,"
    "Nelio Ciguencia <neliomarcos040@gmail.com>",
    "website": "https://odooconcept.com",
    "depends": ["base", "product"],
    "data": [
        # Security
        "security/ir.model.access.csv",
        # Views
        "views/shopping_list_view.xml",
        "views/shopping_list_items_view.xml",
        "views/menu_items.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "OPL-1",
}
