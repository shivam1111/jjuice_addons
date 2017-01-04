from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class nmi_transactions(models.Model):
    _name = 'nmi.transactions'
    
    @api.model
    def create(self,vals):
        sequence = self.env['ir.sequence'].get('NMI') or '/'
        vals['name'] = sequence
        return super(nmi_transactions,self).create(vals)    
    
    name = fields.Char("Serial Number")
    partner_id = fields.Many2one('res.partner',string = "Partner",required = True)