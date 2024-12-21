# -*- coding: utf-8 -*-
from odoo import models, fields, api
from fsspec import filesystem
from odoo.exceptions import UserError

class MinioFileSystem(models.Model):
    _name = 'minio.storage'
    _description = "Minio Storage Configuration"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True, help="A unique code for this storage configuration")
    endpoint_url = fields.Char(string="Endpoint URL", required=True)
    access_key = fields.Char(string="Access Key", required=True)
    secret_key = fields.Char(string="Secret Key", required=True)
    bucket_name = fields.Char(string="Bucket Name", required=True)
    region = fields.Char(string="Region", default="us-east-1")
    is_default_storage = fields.Boolean(string="Is default storage")

    _sql_constraints = [
    ('unique_code', 'unique(code)', 'The code must be unique')
]


    @api.model
    def _get_default_storage(self):
        storage_ids = self.search([('is_default_storage', '=', True)])
        if storage_ids:
            return storage_ids[0]
        return False

    @api.model
    def _get_fs_with_config(self):
        fs = False
        if self.endpoint_url and self.access_key and self.secret_key and self.bucket_name:
            try:
                fs = filesystem("s3", 
                endpoint_url = self.endpoint_url,
                key = self.access_key,
                secret = self.secret_key,
                region = self.region
                )
            except Exception as e:
                raise UserError(f"Error connecting with storage: {e}")
        return fs

    def test_connection(self):
        fs = self._get_fs_with_config()
        if fs:
            try:
                fs.ls(self.bucket_name)
            except Exception as e:
                raise UserError(f"Error accessing bucket: {e}")
        else:
            raise UserError(f"Error getting the filesystem, please check config.")


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def _storage_for_attachment(self):
        storage = self.env['minio.storage']._get_default_storage()
        return storage

    def _get_file(self):
         storage = self._storage_for_attachment()
         if not storage:
             return super()._get_file()
         fs = storage._get_fs_with_config()
         if not fs:
             return super()._get_file()
         try:
             f = fs.open(f'{storage.bucket_name}/{self.store_fname}', 'rb')
         except:
             return super()._get_file()
         return f

    def _set_file(self, content, filename):
         storage = self._storage_for_attachment()
         if not storage:
             return super()._set_file(content, filename)
         fs = storage._get_fs_with_config()
         if not fs:
              return super()._set_file(content, filename)
         try:
            file_name = self._compute_store_fname(filename)
            with fs.open(f'{storage.bucket_name}/{file_name}', 'wb') as f:
                f.write(content)
            self.store_fname = file_name
         except Exception as e:
             raise UserError(f"Error uploading attachment to storage: {e}")
         return super()._set_file(content, filename)