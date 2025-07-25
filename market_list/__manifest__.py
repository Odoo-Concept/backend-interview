{
    "name": "Main App",
    "version": "18.0.1.0.1",
    "category": "Extra Tools",
    "summary": "Módulo integrador para el Proyecto",
    "author": "Erick Birbe <ebirbe@odooconcept.com>, Odoo Concept",
    "website": "https://odooconcept.com",
    "depends": ["base", "product"],
    "data": [
        "security/ir.model.access.csv",
        "views/market_list_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "market_list/static/description/shopping-list.png",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "OPL-1",
}
