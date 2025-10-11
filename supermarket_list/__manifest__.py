# -*- coding: utf-8 -*-
{
    'name': "Supermarket Lists",

    'summary': "Gestión de listas de supermercado con productos, cantidades y estado de compra.",

    'description': """
Módulo para crear y gestionar listas de supermercado:
----------------------------------------------------
- Permite crear listas con nombre y responsable.
- Agregar productos con cantidades deseadas.
- Marcar productos como comprados o no comprados.
- Control de estado de lista: Borrador, En progreso y Completada.
    """,

    'author': "Fernando Fernández",
    'website': "https://www.yourcompany.com",

    'category': 'Productivity',
    'version': '18.0.1.0.0',

    'depends': ['base','product'],

    'data': [
        'security/groups_security.xml',
        'security/ir.model.access.csv',
        'views/supermarket_list_views.xml'
    ],

    'application': True, 
    'installable': True,
    'auto_install': False,
    'sequence': 10,
}
