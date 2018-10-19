from openerp import models, fields, api, _

class shipstation_rate_request_package(models.TransientModel):
    _name = "shipstation.rate.request.package"
    _description = "Shipstation Rate Request Package"
    
    

class shipstation_rate_request(models.TransientModel):
    _name = "shipstation.rate.request"
    _description = "Shipstation Rate Request Wizard"
    
    from_postal_code = fields.Char('Postal Code')
    from_residential = fields.Boolean('Residential',default=False)
    carrier_id = fields.Many2one('carrier.carrier','Carrier')
    service_id = fields.Many2one('carrier.service','Service')
    package_ids = fields.Many2one('carrier.package','Pacakge')
