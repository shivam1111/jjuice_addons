from openerp import models, fields, api, _

class res_partner(models.Model):
    _inherit = "res.partner"
    
    django_id = fields.Integer("Django ID")