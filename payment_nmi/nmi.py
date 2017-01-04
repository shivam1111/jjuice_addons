from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class AcquirerPaypal(models.Model):
    _inherit = 'payment.acquirer'
    
    username = fields.Char(string="NMI Username")
    password = fields.Char(string = "Password")
    