from openerp import models, fields, api, _

class website_banner(models.Model):
    _name = "website.banner"
    _description="Website Banners"
    _inherits = {
            's3.object':'s3_object_id'
    }
    _rec_name = "file_name"
    
    @api.multi
    def unlink(self):
        for rec in self:
            rec.s3_object_id.unlink()
        return super(website_banner,self).unlink()

    @api.multi
    def write(self,vals):
        if vals.get('datas',False):
            for rec in self:
                rec.s3_object_id.datas = vals['datas']
            vals.pop('datas')
        return super(website_banner,self).write(vals)
    
    @api.model
    def create(self,vals):
        if vals.get('datas',False):
            website_banner_key = self.env['ir.config_parameter'].get_param('website_banner_key','website_django')
            s3_object = self.env['s3.object'].with_context(folder_key=website_banner_key).create(vals)
            vals['s3_object_id'] = s3_object.id
        return super(website_banner,self).create(vals)
    
    s3_object_id = fields.Many2one('s3.object','S3 Object',ondelete="cascade",required=True)
    sequence = fields.Integer('Sequence') 