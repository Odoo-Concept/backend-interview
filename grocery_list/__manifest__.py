{
    "name": "Grocery List",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "summary": "Module for creating and managing grocery lists in Odoo.",
    "description": """
Grocery List Module
===================
This module allows users to create and manage grocery lists efficiently.
Users can:
- Create new grocery lists.
- Add products with desired quantities.
- Mark items as purchased (only by the responsible user).
- Manage list states: Draft, In Progress, Completed.
    """,
    "author": "Armando Rojas <armando.rojas@example.com>",
    "website": "https://odooconcept.com",
    "depends": [
        "base",
    ],
    "data": [
        # "security/ir.model.access.csv",
        # "views/grocery_list_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "OPL-1",
}
