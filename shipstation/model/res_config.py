# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.safe_eval import safe_eval
import base64,urlparse,json,requests
from .. import helper

class shipstation_config_settings(osv.osv_memory):
    _inherit = 'integrations.config.settings'

    def get_shipstation_url(self,cr,uid,context={}):
        params = self.pool.get('ir.config_parameter')
        shipstation_debug_mode = safe_eval(params.get_param(cr, uid, 'shipstation_debug_mode',default='False'))
        if shipstation_debug_mode:
               return params.get_param(cr, uid, 'shipstation_test_url',default='')
        else:
               return params.get_param(cr, uid, 'shipstation_url',default='')
        
    def get_shipstation_api_credentials(self,cr,uid,context={}):
        params = self.pool.get('ir.config_parameter')
        shipstation_api_key = params.get_param(cr, uid, 'shipstation_api_key',default='',context=context)
        shipstation_api_secret = params.get_param(cr, uid, 'shipstation_api_secret',default='',context=context)
        return dict(api_key=shipstation_api_key,api_secret=shipstation_api_secret)
    
    def import_carriers(self,cr,uid,ids,context={}):
        myself = self.browse(cr,uid,ids[0],context=context)
        encoded = ":".join([myself.api_key or 'api_key',myself.api_secret or 'api_secret'])
        headers = {
          'Authorization': "Basic "+ base64.b64encode(encoded)
        }
        base_url = self.get_shipstation_url(cr,uid,context)
        url = urlparse.urljoin(base_url,helper.endpoints['list_carriers'])
        response = requests.get(url,headers=headers).json()
        for carrier in response:
            fields = helper.carrier_carrier_map.values()
            fields.append('id')
            c = self.pool.get('carrier.carrier').search_read(cr,uid,[('code','=',carrier['code'])],fields=fields,limit=1)
            vals = {}
            for x,y in helper.carrier_carrier_map.iteritems():
                vals.update({y:carrier.get(x)})
            if len(c) > 0:
                #Just overwrite
                id = c[0]['id']
                del c[0]['id']
                for key,val in c.pop().iteritems():
                    self.pool.get('carrier.carrier').write(cr,uid,id,vals,context)
            else:
                #Create a new carrier
                self.pool.get('carrier.carrier').create(cr,uid,vals,context)
                
                
        
    def set_default_api_key(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        myself = self.browse(cr,uid,ids[0],context=context)
        params.set_param(cr, uid, 'shipstation_api_key', (myself.api_key or '').strip(), groups=['base.group_system'], context=None)

    def get_default_api_key(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        shipstation_api_key = params.get_param(cr, uid, 'shipstation_api_key',default='',context=context)        
        return dict(api_key=shipstation_api_key)
    
    def set_default_api_secret(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        myself = self.browse(cr,uid,ids[0],context=context)
        params.set_param(cr, uid, 'shipstation_api_secret', (myself.api_secret or '').strip(), groups=['base.group_system'], context=None)

    def get_default_api_secret(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        shipstation_api_secret = params.get_param(cr, uid, 'shipstation_api_secret',default='',context=context)        
        return dict(api_secret=shipstation_api_secret)    
    
    def set_default_url(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        myself = self.browse(cr,uid,ids[0],context=context)
        params.set_param(cr, uid, 'shipstation_url', (myself.url or '').strip(), groups=['base.group_system'], context=None)

    def get_default_url(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        shipstation_url = params.get_param(cr, uid, 'shipstation_url',default='',context=context)        
        return dict(url=shipstation_url)        

    def set_default_test_url(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        myself = self.browse(cr,uid,ids[0],context=context)
        params.set_param(cr, uid, 'shipstation_test_url', (myself.test_url or '').strip(), groups=['base.group_system'], context=None)

    def get_default_test_url(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        shipstation_test_url = params.get_param(cr, uid, 'shipstation_test_url',default='',context=context)        
        return dict(test_url=shipstation_test_url)            

    def set_default_debug_mode(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        myself = self.browse(cr,uid,ids[0],context=context)
        params.set_param(cr, uid, 'shipstation_debug_mode', repr(myself.debug_mode))

    def get_default_debug_mode(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        shipstation_debug_mode = params.get_param(cr, uid, 'shipstation_debug_mode',default='False',context=context)        
        return dict(debug_mode=safe_eval(shipstation_debug_mode))                

    _columns = {
                'api_key':fields.char('API KEY'),
                'api_secret':fields.char('API SECRET'),
                'url':fields.char('URL'),
                'test_url':fields.char('Test URL'),
                'debug_mode':fields.boolean('Debug Mode')
            }