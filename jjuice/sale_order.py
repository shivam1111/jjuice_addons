# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID, api
from operator import itemgetter
import operator
from openerp.exceptions import except_orm
from collections import OrderedDict
from _symtable import FREE

class sale_order(models.Model):
    _inherit  = "sale.order"
    _description = "Sale Order JJuice"
    
    def confirm_sales_order(self,cr,uid,sale_id,paid_line,context=None):
        if context == None:context = {}
        sale_order = self.pool.get('sale.order')
        plan_id = self.pool.get('payment.plan').create(cr,uid,{'amount':paid_line.get('paid',False),
                                                               'order_id':sale_id,
                                                               'method_of_payment':paid_line.get('method_of_payment',False),
                                                               'amount_original':paid_line.get('paid',False)
                                                               },
                                                                 context)
        account_invoice = self.pool.get('account.invoice')
        sale_order.action_button_confirm(cr,uid,[sale_id],context)
        invoice_wizard = self.pool.get('sale.advance.payment.inv')
        wizard_id = invoice_wizard.create(cr,uid,{'advance_payment_method':'all'},context)
        context.update({'active_ids':[sale_id],'open_invoices':True})
        res = invoice_wizard.create_invoices(cr,uid,[wizard_id],context)
        account_invoice.signal_workflow(cr, uid, [res.get('res_id',False)], 'invoice_open')
        inv = account_invoice.browse(cr,uid,res.get('res_id',False),context)
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'jjuice', 'view_vendor_receipt_dialog_form_jjuice')
        dummy, invoice_view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'invoice_form')
        res.update({'invoice_view_id':invoice_view_id})
        invoice_info = {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'plan_id':plan_id,
                'invoice_open':True,
                'payment_expected_currency': inv.currency_id.id,
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                'default_amount': paid_line.get('paid',False),
                'default_reference': inv.name,
                'close_after_process': True,
                'invoice_type': inv.type,
                'default_journal_id':paid_line.get('method_of_payment',False),
                'invoice_id': inv.id,
                'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }
        return {'res':res,'plan_id':plan_id,'invoice_info':invoice_info}
        
    def _get_product_conc_vol(self,cr,uid,attribute,product_id,context):
        ''' 
        Takes in attributes ids of volume and concentration in the order respectively and products id
        and return the name and id of the attribute values that are present from that attribute in this product
        '''   
        
        cr.execute('''
        select DISTINCT ON (att_id) att_id,child.name,prodattr.id,child.default_free_samples from  product_attribute_value_product_product_rel as base
            left join product_attribute_value as child on base.att_id = child.id  
                left join product_attribute as prodattr on child.attribute_id = prodattr.id
                    where base.prod_id = %s and (child.attribute_id = %s or child.attribute_id = %s) 

        ''' %(product_id,attribute[0],attribute[1]))
        
        res = cr.fetchall();
        return res
        
    @api.multi
    @api.depends('name',)
    def _compute_payments(self):
        for record in self:
            obj=self.env['payment.plan']
            search_id=obj.search([('order_id', '=' ,record.id)])
            record.payment_plan_ids=search_id
    
    
    def print_attachment_report(self,cr,uid,id,context=None):
        uid = SUPERUSER_ID
        assert len(id) == 1
        vals = [] #contains the products that have concentration and volume
        misc = {} #contains the miscelaneous products
        free = [] # contains the free products
        vol,conc = [],[]
        strength = {}
        strength_misc = 0
        strength_free = {}
        strength_marketing = 0
        marketing = {}
        conc_dict = OrderedDict()
        vol_dict = {}
        paid_stamp,shipping_stamp = True,True
        
        if type(id) is int: id = [id]
        invoice_lines = {'total':0.00,'paid':0.00,'residual':0.00,'invoice':{}}
        cr.execute('''
            select id from product_product where shipping =true limit 1
        ''')
        shipping_product_id = cr.fetchone()[0]
        brw = self.browse(cr,uid,id[0],context)
        dummy, vol_id_attribute = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'jjuice', 'attribute_vol')
        dummy, conc_id_attribute = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'jjuice', 'attribute_conc')
        attribute = [vol_id_attribute,conc_id_attribute]
        comment = brw.note
        grand_total = 0

        #Collecting related invoice information
        for invoice  in brw.invoice_ids:
            #Checking for the paid_stamp
            if invoice.state != 'cancel':
                if invoice.state != 'paid':
                    paid_stamp = False
                invoice_lines['invoice'].update({
                                        invoice.number or invoice.state:{'total':invoice.amount_total,'residual':invoice.residual,'paid':invoice.amount_total - invoice.residual}
                                     })
                invoice_lines['total'] =  invoice_lines['total'] +  invoice.amount_total
                invoice_lines['residual'] = invoice_lines['residual'] +  invoice.residual
                invoice_lines['paid'] = invoice_lines['paid'] + (invoice.amount_total - invoice.residual)
                 
        name_list = []
        for line in brw.order_line:
            #Checking for marketing products
            if line.product_id.market_case:
                if line.product_id.name in marketing.keys():
                    marketing[line.product_id.name] = marketing[line.product_id.name] +  line.product_uom_qty
                else: marketing.update({line.product_id.name:line.product_uom_qty})
                strength_marketing = strength_marketing + line.product_uom_qty
                continue            

            #Checking for the shipping stamp
            if line.product_id.id == shipping_product_id:
                if line.product_uom_qty > 0:
                    shipping_stamp = False
                    
            if line.product_id.misc:
                if line.product_id.name in misc.keys():
                    misc[line.product_id.name] = misc[line.product_id.name] +  line.product_uom_qty
                else:misc.update({line.product_id.name:line.product_uom_qty})
                strength_misc = strength_misc + line.product_uom_qty
                continue
            
            elif line.product_id.shipping or line.product_id.market_case:  
                continue
            else:
                product_info = self._get_product_conc_vol(cr,uid,attribute,line.product_id.id,context)
#             Output [(att_id,product_attribute_value.name,product_attribute.id)] ---> product_info
                for i in product_info:
                    if i[2] == vol_id_attribute:
                        vol = i
                        if not i[0] in vol_dict:
                            vol_dict.update({i[0]:i[1]})
                    elif i[2] == conc_id_attribute:
                        conc = i
                        if not i[0] in conc_dict:
                            conc_dict.update({
                                              i[0]:i[1]
                                              })
                    
                if line.price_unit == 0 and vol[3]:
                    if not conc[0] in strength_free:
                        strength_free.update({
                                              conc[0]:line.product_uom_qty
                                              })
                    else:
                        strength_free[conc[0]] = strength_free[conc[0]] + line.product_uom_qty
                        
                         
                    if not line.product_id.product_tmpl_id.product_tmpl_id.id in free:
                        free.append({
                                     'id':line.product_id.product_tmpl_id.product_tmpl_id.id,
                                     'name':line.product_id.product_tmpl_id.product_tmpl_id.name,
                                     'conc':{conc[0]:line.product_uom_qty}
                                     })
                    else:
                        #find the index
                        for i in free:
                            if i['id'] == line.product_id.product_tmpl_id.product_tmpl_id.id:
                                index = i
                                index.get('conc').update({
                                                             conc[0]:line.product_uom_qty
                                                             })
                    continue
                if not vol[0] in strength:
                    strength.update({
                                    vol[0]:{
                                            conc[0]:line.product_uom_qty,
                                            }
                                    })
                else:
                    
                    if strength.get(vol[0],False).get(conc[0],False):
                        strength.get(vol[0],False)[conc[0]] = strength.get(vol[0],False).get(conc[0],False) + line.product_uom_qty
                    else:
                         strength.get(vol[0],False).update({
                                                            conc[0]:line.product_uom_qty
                                                            }) 
                         
                grand_total = grand_total + line.product_uom_qty
                if not line.product_id.product_tmpl_id.product_tmpl_id.id in name_list:
                    name_list.append(line.product_id.product_tmpl_id.product_tmpl_id.id)
                    if not line.product_id.product_tmpl_id.product_tmpl_id.id:
                        raise except_orm(_('Error!'),_('Check Product Configuration with id-: %s and name-:%s')%(line.product_id.id,line.product_id.name))
                    vals.append({
                                     'id':line.product_id.product_tmpl_id.product_tmpl_id.id,
                                     'name':line.product_id.product_tmpl_id.product_tmpl_id.name,
                                      vol[0]:{
                                             'vol_name':vol[1],
                                             'conc':{
                                                     conc[0]:line.product_uom_qty
                                                 }
                                             }
                                         })
                else:
                    #find the index of flavour in the list
                    index = {}
                    for i in vals:
                        if i['id'] == line.product_id.product_tmpl_id.product_tmpl_id.id:
                            index = i
                    if index.get(vol[0],False):
                        if index[vol[0]].get('conc',False) and index[vol[0]].get('conc',False).get(conc[0],False):
                            index[vol[0]].get('conc',False)[conc[0]] = index[vol[0]].get('conc',False)[conc[0]] + line.product_uom_qty
                        else:index[vol[0]].get('conc',{}).update({
                                                      conc[0]:line.product_uom_qty
                                                      })
                    else:
                        index.update({
                                     vol[0]:{
                                             'vol_name':vol[1],
                                             'conc':{
                                                    conc[0]:line.product_uom_qty 
                                                 }
                                         }
                                     })
        free = sorted(free,key=itemgetter('name'))
        vals = sorted(vals,key=itemgetter('name'))
        buffer_dict = {}
        buffer_dict1  = conc_dict.copy()
        for i  in buffer_dict1:
            try:
                buffer_dict.update({i:int(conc_dict[i].split('mg')[0])})
                del conc_dict[i]
            except ValueError:
                print "The element does not have nany numerical concentration"
        del buffer_dict1
        for key,value in sorted(buffer_dict.items(),key=operator.itemgetter(1),reverse=True):
            conc_dict.update({key:str(value)+"mg"})
        data= {'paid_stamp':paid_stamp,'shipping_stamp':shipping_stamp,'invoice_line':invoice_lines,
                                 'ids':id,'grand_total':grand_total,
                                 'comment':comment,'strength_misc':strength_misc,
                                 'strength':strength,'conc_dict':conc_dict.items(),'vol_dict':vol_dict,'vals':vals,'misc':misc,'free':free,
                                 'strength_free':strength_free,
                                 'strength_marketing':strength_marketing,
                                 'marketing':marketing,
                                 }

        if context.get('stock_picking',False):
            data.update({'model':'stock.picking'})
            return {
                        'type': 'ir.actions.report.xml',
                        'report_name': 'jjuice.report_qweb_order_attachment',
                        'context':context,
                        'datas': {'model':'stock.picking','data':data}
                        }
        else:            
            return {
                        'type': 'ir.actions.report.xml',
                        'report_name': 'jjuice.report_qweb_order_attachment',
                        'context':context,
                        'datas':{'model':'sale.order','data':data}
                    }
    
    field_order_html = fields.Html("Order")
    payment_plan_ids=fields.Many2many("payment.plan","payment_id","payment_sale_relation","sale_id","Payment Plan Id",compute='_compute_payments')
