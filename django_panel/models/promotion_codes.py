from openerp import models, fields, api, _
from openerp.exceptions import except_orm

class promotion_codes(models.Model):
    _name = "promotion.codes"
    _description = "Promotion Codes"

    name = fields.Char('Promotion Code',required = True)
    description = fields.Text('Description')
    sequence = fields.Integer("Sequence")
