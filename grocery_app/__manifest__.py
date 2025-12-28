{
    'name': 'Grocery App',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Manage grocery shopping lists with products and purchase tracking',
    'description': """
Grocery App - Grocery List Management Module
=============================================
This module enables users to create, manage, and track grocery shopping lists
in a structured and user-friendly manner.

Key Features:
-------------
* Create and manage grocery lists with responsible users
* Add products to lists with quantities
* Track purchase status of items
* Automatic status updates based on item completion
* Role-based access control for purchase status updates
* Clean workflow: Draft -> In Progress -> Completed
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['base', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'security/grocery_list_security.xml',
        'views/grocery_list_views.xml',
        'views/grocery_list_item_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
