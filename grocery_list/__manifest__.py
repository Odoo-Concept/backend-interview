{
    "name": "Grocery List",
    "version": "18.0.1.0.1",
    "category": "Extra Tools",
    "summary": "Gestión de listas de supermercado",
    "description": """
        Módulo para crear y gestionar listas de supermercado.
        Permite crear listas, añadir productos, indicar cantidades
        y marcar productos como comprados.
    """,
    "author": "Johan Rujano @jrujano",
    "depends": ["base", "product"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/grocery_list_views.xml",
        "views/grocery_list_item_views.xml",
        "views/menu_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "OPL-1",
}
