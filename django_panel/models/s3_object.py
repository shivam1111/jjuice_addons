from openerp import models, fields, api, _
from helpers import put_object_bucket,get_bucket_location,get_object_bucket,get_url,delete_object_bucket
from openerp.exceptions import except_orm
import urlparse,hashlib

class s3_object(models.Model):
    _name = "s3.object"
    _description = "Single S3 Object"
    _rec_name = "file_name"
    
    @api.multi
    @api.depends('datas')
    def _data_get(self):
        root_bucket = self.env['ir.config_parameter'].get_param('root_bucket','jjuice-django')
        folder_key = self.folder_key or '/'
        location =  get_bucket_location(self,root_bucket)
        try:
            read = get_object_bucket(location,folder_key,self.store_fname)
            self.datas = read
        except AssertionError as e:
            raise except_orm('Error!',e)
            
    def _data_set(self):
        assert self.env.context.get('folder_key',False) or self.folder_key , "Sorry the folder path is not present"
        root_bucket = self.env['ir.config_parameter'].get_param('root_bucket','jjuice-django')
        folder_key = self.env.context.get('folder_key',self.folder_key)
        location =  get_bucket_location(self,root_bucket)
        bucket_location  = self.env['ir.config_parameter'].get_param('aws_base_url')
        try:
            if self.store_fname:
                delete_object_bucket(location,folder_key,self.store_fname)
            fname = put_object_bucket(location,folder_key,self.datas)
            self.store_fname = fname
            self.url = get_url(bucket_location,root_bucket,folder_key,fname)
            self.folder_key = folder_key
        except AssertionError as e:
            raise except_orm('Error!',e)

    @api.multi
    def unlink(self):
        for rec in self:
            root_bucket = self.env['ir.config_parameter'].get_param('root_bucket','jjuice-django')
            folder_key = self.folder_key or '/'
            location =  get_bucket_location(self,root_bucket)
        try:
            delete = delete_object_bucket(location,folder_key,self.store_fname)
        except AssertionError as e:
            raise except_orm('Error!',e)            
        return super(s3_object,self).unlink()
    
    file_name = fields.Char('File Name',required=True)
    datas =  fields.Binary(compute=_data_get, inverse=_data_set, string='File Content', nodrop=True)
    store_fname = fields.Char('Stored Filename')
    url =  fields.Char('File URL')
    folder_key = fields.Char('Folder Key')