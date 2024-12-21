{
    'name': 'Odoo MinIO S3 Storage',
    'version': '1.0',
    'summary': 'Connect Odoo to MinIO using S3.',
    'description': 'This module allows you to store Odoo attachments in MinIO using S3.',
    'author': 'Tu Nombre',
    'website': 'https://tudominio.com',
    'license': 'LGPL-3',
    'depends': ['base'],  # Dependencia obligatoria de Odoo
    'data': [ # Archivos de datos
        'views/minio_storage_views.xml',
         'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}