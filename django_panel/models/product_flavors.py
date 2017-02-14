from openerp import models, fields, api, _
from helpers import BinaryS3Field,delete_object_bucket,get_bucket_location
from openerp.exceptions import except_orm

class product_flavors(models.Model):
    _inherit = "product.flavors"
    _description = "Product Flavors Image"
    _order = "sequence"
    
    @api.multi
    def unlink(self):
        for rec in self:
            try:
                root_bucket = self.env['ir.config_parameter'].get_param('root_bucket','jjuice-django')
                assert root_bucket, "Sorry the root bucket is not available" 
                access_key_id = self.env['ir.config_parameter'].get_param('aws_access_id')
                secret_access_key = self.env['ir.config_parameter'].get_param('aws_secret_key')
                assert access_key_id and secret_access_key, "Invalid Credentials"
                delete_object_bucket(self._table,self.id,access_key_id,secret_access_key,root_bucket)
            except AssertionError as e:
                raise except_orm('Error',e)
        return super(product_attribute_value,self).unlink()

    file_name = fields.Char(string = "File Name")
    datas = BinaryS3Field(string = "Image",key_name = False)    
    sequence = fields.Integer(string="Sequence")
    short_description = fields.Text('Short Description')
    long_description = fields.Text('Long Description')
    review_ids = fields.One2many('flavor.reviews','flavor_id','Reviews')