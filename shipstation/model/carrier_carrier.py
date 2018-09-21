from openerp import models, fields, api, _

class carrier_carrier(models.Model):
    _name = "carrier.carrier"
    _description = "Carriers"
    
    _sql_constraints = [('code_unique','unique(code)','Carrier Code should be unqie')]
    
    name = fields.Char('Name',required=True)
    code = fields.Char('Code',required=True,readonly = True)
    account_no = fields.Char('Account No.', readonly = True)
    requires_funded_account = fields.Boolean('Required Funded Account',readonly=True)
    balance = fields.Float('Balance',readonly = True)
    shipping_provider_id = fields.Char('Shipping Provider ID',readonly=True)
    primary = fields.Boolean('Primary',readonly = True)
    