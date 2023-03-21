# -*- coding: utf-8 -*-
{
    'name': 'Product Supplier',
    'version': '1.0',
    'summary': 'product supplier',
    'description': "product supplier",
    'website': 'http://www.baidu.com',
    'depends': ['base'],
    'category': 'Budget',
    'sequence': 1,
    'demo': [],
    'data': [
        # 'data/data.xml',
        'security/ir.model.access.csv',
        'views/product_supplier.xml'
    ],
    'qweb': [
        "static/src/xml/*.xml"
    ],
    'assets': {
            'web.assets_backend': [
                'product_supplier/static/src/js/product_supplier.js',
            ],
            'web.assets_qweb': [
                'product_supplier/static/src/xml/product_supplier.xml',
            ],
        },
    'installable': True,
    'application': True,
    'auto_install': False,
}