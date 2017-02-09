from openerp import models, fields, api, _

class website_policy(models.Model):
    _name = "website.policy"
    _description="Website Policy"
    _inherits = {
            's3.object':'s3_object_id'
    }

    @api.multi
    def unlink(self):
        for rec in self:
            rec.s3_object_id.unlink()
        return super(website_policy,self).unlink()

    @api.multi
    def write(self,vals):
        if vals.get('datas',False):
            for rec in self:
                rec.s3_object_id.datas = vals['datas']
            vals.pop('datas')
        return super(website_policy,self).write(vals)
    
    @api.model
    def create(self,vals):
        if vals.get('datas',False):
            website_policy_key = self.env['ir.config_parameter'].get_param('website_policy_key','website_django')
            s3_object = self.env['s3.object'].with_context(folder_key=website_policy_key).create(vals)
            vals['s3_object_id'] = s3_object.id
        return super(website_policy,self).create(vals)
    
    s3_object_id = fields.Many2one('s3.object','S3 Object',ondelete="cascade",required=True)
    sequence = fields.Integer('Sequence') 
    name = fields.Char('Name',required=True)
    description = fields.Text('Description')