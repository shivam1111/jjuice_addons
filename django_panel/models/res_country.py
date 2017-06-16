from openerp import models, fields, api, _

class res_country_state(models.Model):
    _inherit = "res.country.state"

    is_banned = fields.Boolean('Is Banned',help="If true then this state will not appear in the list for shipment as it is banned to sell here.")

class res_country(models.Model):
    _inherit = "res.country"
    
    is_shipping_allowed = fields.Boolean('Is Shipping Allowed')