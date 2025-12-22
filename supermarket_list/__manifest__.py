{
    "name": "Supermarket Lists",
    "version": "18.0.1.0.1",
    "category": "Productivity",
    "summary": "Create and manage supermarket shopping lists.",
    "icon": "/supermarket_list/static/description/icon.png",
    "author": "Raulerf",
    "website": "https://github.com/Raulerf",
    "depends": [
        "base",
        "portal",
        "website",
    ],
    "data": [
        "security/supermarket_list_security.xml",
        "security/ir.model.access.csv",
        "views/supermarket_list_views.xml",
        "views/supermarket_list_menus.xml",
        "views/portal_supermarket_list_templates.xml",
    ],
    "demo": [
        "demo/supermarket_list_demo.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "OPL-1",
}
