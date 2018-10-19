from openerp import models, fields, api, _
from .. import helper
from openerp.exceptions import Warning

class carrier_package(models.Model):
    _name = "carrier.package"
    _description = "Carrier Package"

    _sql_constraints = [('code_unique','unique(code)','Carrier Service Code should be unqie')]
    
    name = fields.Char('Name')
    code = fields.Char('Code')
    domestic = fields.Boolean('Domestic')
    international = fields.Boolean('International')
    carrier_id = fields.Many2one('carrier.carrier','Carrier')    
    

class carrier_service(models.Model):
    _name = "carrier.service"
    _description = "Carrier Service"
    _sql_constraints = [('code_unique','unique(code)','Carrier Service Code should be unqie')]
    
    name = fields.Char('Name')
    code = fields.Char('Code')
    domestic = fields.Boolean('Domestic')
    international = fields.Boolean('International')
    carrier_id = fields.Many2one('carrier.carrier','Carrier')

class carrier_carrier(models.Model):
    _name = "carrier.carrier"
    _description = "Carriers"
    
    _sql_constraints = [('code_unique','unique(code)','Carrier Code should be unqie')]
    
    @api.one
    def update_packages(self):
        params = self.env['integrations.config.settings'].get_shipstation_api_credentials()
        params.update({
                'code':self.code,
                'base_url':self.env['integrations.config.settings'].get_shipstation_url()
            })        
        response = helper.list_packages(**params)
        if response.status_code == 200:
#             carrier_service_map
            for p in response.json():
                # First search if the package exists
                package = self.env['carrier.package'].search([('code','=',p.get('code'))])
                if len(package) > 0:
                    # Package already exists. Just update values
                    vals = helper.map_field(helper.carrier_package_map,p)
                    package.write(vals)
                else:
                    # Create a new package
                    vals = helper.map_field(helper.carrier_package_map,p)
                    self.write({
                            'package_ids':[(0,0,vals)]
                        })
        else:
            raise Warning(response.status_code,response.text)        
    
    @api.one
    def update_services(self):
        params = self.env['integrations.config.settings'].get_shipstation_api_credentials()
        params.update({
                'code':self.code,
                'base_url':self.env['integrations.config.settings'].get_shipstation_url()
            })        
        response = helper.list_services(**params)
        if response.status_code == 200:
#             carrier_service_map
            for p in response.json():
                # First search if the package exists
                service = self.env['carrier.service'].search([('code','=',p.get('code'))])
                if len(service) > 0:
                    # Package already exists. Just update values
                    vals = helper.map_field(helper.carrier_service_map,p)
                    service.write(vals)
                else:
                    # Create a new package
                    vals = helper.map_field(helper.carrier_service_map,p)
                    self.write({
                            'service_ids':[(0,0,vals)]
                        })
        else:
            raise Warning(response.status_code,response.text)
    
    @api.one
    def update_info(self):
        params = self.env['integrations.config.settings'].get_shipstation_api_credentials()
        params.update({
                'code':self.code,
                'base_url':self.env['integrations.config.settings'].get_shipstation_url()
            })
        response = helper.get_carrier(**params)
        if response.status_code == 200:
            vals = helper.map_field(helper.carrier_carrier_map,response.json())
            self.write(vals)
        else:
            raise Warning(response.status_code,response.text)
            
    name = fields.Char('Name',required=True)
    code = fields.Char('Code',required=True,readonly = True)
    account_no = fields.Char('Account No.', readonly = True)
    requires_funded_account = fields.Boolean('Required Funded Account',readonly=True)
    balance = fields.Float('Balance',readonly = True)
    shipping_provider_id = fields.Char('Shipping Provider ID',readonly=True)
    primary = fields.Boolean('Primary',readonly = True)
    active = fields.Boolean('Active',default=True)
    service_ids = fields.One2many('carrier.service','carrier_id','Services')
    package_ids = fields.One2many('carrier.package','carrier_id','Packages')

    