# __manifest__.py
{
    'name': 'Supermarket List',
    'version': '1.0',
    'summary': 'Modulo de ejemplo para Odoo',
    'author': 'kouzte',
    'depends': ['base', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/supermarket_list_views.xml',
    ],
    'installable': True,
    'application': True,
}
