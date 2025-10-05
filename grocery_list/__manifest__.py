{
    "name": "Grocery List",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "summary": "Create and manage grocery lists with items, quantities, and purchase tracking.",
    "description": """
Grocery List Module
===================
This module allows users to create and manage grocery lists efficiently.

Features:
- Create grocery lists with a responsible user and states.
- Add products.
- Only the responsible can mark items as purchased.
- States: Draft, In Progress, Completed.
    """,
    "author": "Armando Rojas <armando.rojas@example.com>",
    "website": "https://odooconcept.com",
    "depends": [
        "base",
        "mail",
        "product",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "security/rules.xml",
        "views/grocery_list_views.xml"
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
