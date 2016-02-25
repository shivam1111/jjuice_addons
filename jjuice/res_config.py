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
from openerp.tools.translate import _

class stock_config_settings(osv.osv_memory):
    _inherit = 'stock.config.settings'

    def get_default_volume_show(self,cr,uid,ids,context=None):
        cr.execute('''
            select id from product_attribute_value where default_free_samples = true
        ''')
        attribute_id = cr.fetchall()
        if attribute_id:
            return {'volume_show':attribute_id[0][0]}
        else : 
            return {'volume_show':False}
        
    def set_default_volume_show(self, cr, uid, ids, context=None):
        obj = self.read(cr,uid,ids[0],['volume_show'],context)
        if obj.get('volume_show',False):
            cr.execute('''
                update product_attribute_value set default_free_samples = false where default_free_samples = true;update product_attribute_value set default_free_samples = true where id = %s;
                ''' %(obj.get('volume_show',False)[0]))
            
    _columns = {
                'volume_show':fields.many2one("product.attribute.value","Volume",help = "Volume for which the free samples are distributed for sales promotion\
                In case the volume attribute is not entered no product will be displayed")
                }
