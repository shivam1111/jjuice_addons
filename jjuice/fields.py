from openerp.osv import fields, osv 
from openerp.tools.translate import _
from openerp.addons.crm import crm
from openerp.addons.base.res.res_partner import format_address
from openerp import SUPERUSER_ID

crm.AVAILABLE_PRIORITIES = [
    ('0', 'Very Low'),
    ('1', 'Low'),
    ('2', 'Normal'),
    ('3','High'),
    ('4', 'Very High'),
    ('5','Very Very High')
]

FINANCE_CLASSIFY  = [
                 ('retailer','Retailer'),
                 ('wholesale','Wholesaler / Distributer'),
                 ('private_label','Private Label'),
                 ('website','Vapejjuice.com'),
                 ]

ACCOUNT_TYPE  = [('smoke_shop',"Smoke Shop"),('vape_shop','Vape Shop'),('convenient_gas_store','Convenient Store/ Gas Station'),
                 ('website','Online Store'),
                 ]


class crm_lead(format_address, osv.osv):
    _inherit = 'crm.lead'
    
    def trasnfer_leads_partners(self,cr,uid,ids,context):
        partner = self.pool.get('res.partner')
        leads = self.pool.get('crm.lead')
        lead_ids = leads.search(cr,uid,['|', ('type','=','lead'), ('type','=',False)],context=context)
        for i in  leads.browse(cr,uid,lead_ids,context):
            use_parent_address = False
            company_vals = {}
            contact_vals = {}
            comment = ""
            company_id = False
            comment = comment+ "Subject: %s\n"%(i.name)
            if i.referred:
                comment = comment + "Referred By: %s\n"%(i.referred)
            #Check if there is a company
            if i.partner_name:
                use_parent_address = True
                company_vals.update({
                                    'name':i.partner_name,
                                    'is_company':True,
                                    'user_id': i.user_id and i.user_id.id or False,
                                    'leads':True,
                                    'phone':i.phone,
                                    'mobile':i.mobile,
                                    'fax':i.fax,
                                    'email':i.email_from,
                                    'street':i.street,
                                    'street2':i.street2,
                                    'city':i.city,
                                    'state_id':i.state_id and i.state_id.id or False,
                                    'zip':i.zip,
                                    'country_id':i.country_id and i.country_id.id or False,
                                    'date_field':i.date_field,
                                    'lead_type':i.lead_type,
                                    'how_met':i.how_met,
                                    'function':i.function,
                                    'priority':i.priority,
                                    'comment':comment,
                                    'type':'contact',
                                    'customer':False,
                                    
                                })
                company_id = partner.create(cr,uid,company_vals,context)
            if i.contact_name:
                contact_vals.update({
                                     'name':i.contact_name,
                                     'type':'contact',
                                     'customer':False,
                                     'comment':comment,
                                     'is_company':False,
                                     'user_id': i.user_id and i.user_id.id or False,
                                     'use_parent_address':use_parent_address,
                                     'leads':True,
                                     'phone':i.phone,
                                     'mobile':i.mobile,
                                     'fax':i.fax,
                                     'email':i.email_from,
                                     'date_field':i.date_field,
                                     'lead_type':i.lead_type,
                                     'how_met':i.how_met,
                                     'function':i.function,
                                     'priority':i.priority,
                                     'parent_id':company_id,
                                     })
                partner.create(cr,uid,contact_vals,context)
        return True
    
    
    _columns = {
                'priority': fields.selection(crm.AVAILABLE_PRIORITIES, 'Priority', select=True),
                }
    
 # this class are used for adding field in employee 
class hr_employee(osv.osv):
    _inherit='hr.employee'
    _description='jjuice module'
    _columns={
                
           # 'personal_email': fields.char('personal Email', size=240),
            'photo_dl':fields.binary('Photo of Driver License'),
            'skype_id': fields.char('Skype Id', size=240),
 }
    # this method is use for creating commission when employee create ,commission will automatic created when employee will create
    '''def create(self,cr,uid,vals,context=None):
        vals.get('name')
        obj=self.pool.get('commission.employee')
         
        id=super(hr_employee,self).create(cr,uid,vals,context)
        obj.create(cr,uid,{'name':id,'active':True},context)
        return id'''     
    
class res_partner(osv.osv):
    _inherit='res.partner'
    _description='JJUICE'
    
    def convert_lead_partner(self,cr,uid,ids,context):
        for i in ids:
            child_ids = self.search(cr,uid,[('parent_id','child_of',i)])
            self.write(cr,uid,child_ids,{
                                            'customer':True,
                                            'leads':False
                                         },context)
    
    def create(self,cr,uid,vals,context):
        return super(res_partner,self).create(cr,uid,vals,context)
    
    _columns={
        'skype_id': fields.char('Skype Id', size=240),
        'resale_no': fields.char('State Issued Resale Number', size=240),
        'acccount_type':fields.selection (ACCOUNT_TYPE,string = "Type Of Account"),
        'classify_finance':fields.selection(FINANCE_CLASSIFY,string="Account Classification(For Finance)"),
        'm2m':fields.one2many("partner.lead",'partner2'),
        'date_field':fields.date('Date we first met'),
        'lead_type':fields.selection([('Hot Lead','Hot Lead'),('Warm Lead','Warm Lead'),('Still No Contact','Still No Contact'),('60-90 Days','60-90 Days'),('Not Interested','Not Interested')],string="Type of Lead"),
        'how_met':fields.text('How we met'),
        'priority':fields.selection(crm.AVAILABLE_PRIORITIES,'Priority')
        }
    
class res_partner_lead(osv.osv):
    _name='partner.lead'
    _columns={'notes':fields.text("Notes"),
              'display_partner':fields.many2one("res.partner","Account"),
              'display_lead':fields.many2one("crm.lead","Leads"),
              'partner2':fields.many2one("res.partner"),
              'lead2':fields.many2one("crm.lead"),
              
              }
class crm_lead(osv.osv):
    _inherit='crm.lead'
    _description='jjuice module'
    
    _columns={
              'account_type':fields.selection(ACCOUNT_TYPE,string="Type Of Account"),
              'primary_name':fields.char('Primary Contact Name & Title'),
              'primary_phone':fields.char('Primary Contact phone#'),
              'primary_email':fields.char('Primary Contact email'),
              '2nd_name':fields.char('(if) 2nd Point of Contact & Title'),
              '2nd_phone':fields.char('(if) 2nd Point of Contact Phone #'),
              '2nd_email':fields.char('(if) 2nd Point of Contact email'),
              'date_field':fields.date("Date We First Met"),
              'how_met':fields.text('How We Met'),
              'lead_type':fields.selection([('Hot Lead','Hot Lead'),('Warm Lead','Warm Lead'),('Still No Contact','Still No Contact'),('60-90 Days','60-90 Days'),('Not Interested','Not Interested')],string="Type of Lead"),
              'logs':fields.one2many("partner.lead",'lead2'),
              }
class update_product(osv.osv):
    _name='update.product'
    _description='product module'
    _columns={
              'product_name':fields.many2one('product.product','Product'),
              'product_id':fields.many2one('product.wizard','product_id'),
             # 'cost_price':fields.float('Cost Price'),
               'cost_price':fields.float(string="Cost Price"),
              }
    
    def update_product(self,cr,uid,ids,product_name,context=None):
        obj=self.pool.get('product.product').browse(cr,uid,product_name).standard_price
        res={}
        res['cost_price']=obj
        return {'value':res}
    
    def create(self,cr,uid,vals,context=None):
        obj=self.pool.get('product.product') 
        id=vals.get('product_name')
        price=vals.get('cost_price')
        obj.write(cr, uid, id, {'standard_price':price}, context)
        ids=super(update_product,self).create(cr,uid,vals,context)
        return ids     
    

    
        
class sale_order(osv.osv):
    _inherit='sale.order'
    _description='jjuice module'
    
    def function_commission(self,cr,uid,ids,commission,args,Context=None):
         res={}
         obj1=self.browse(cr,uid,ids)
         if obj1.internal_sale:
             for i in ids:
                 obj=self.browse(cr,uid,i).order_line
                 sum=0
             for j in obj:
                 sum=sum + j.commission
             res[i]=0
             return res
         else:
             for i in ids:
                 obj=self.browse(cr,uid,i).order_line
                 sum=0
                 for j in obj:
                     sum=sum + j.commission
                 res[i]=sum
                 return res
    
    _columns={
              'shipment':fields.char('Shipment',size=240),
              'sale_rep':fields.many2many('commission.employee','commission_emp_relation','sale_id','emp_id','Sales Rep(s)'),
              't_commission':fields.function(function_commission,type='float',string='Total Commission'),
              'internal_sale':fields.boolean('Internal Sale'),
              'state': fields.selection([
            ('draft', 'Consignment'),
            ('sent', 'Consignment Mailed'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sale Order'),
            ('manual', 'Approved'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done')]),
              }
    def action_wait(self, cr, uid, ids, context=None):
        uid = SUPERUSER_ID
        obj=self.browse(cr,uid,ids)
        
        if obj.internal_sale:
            method_return=super(sale_order,self).action_wait(cr,uid,ids,context)
        else:
            try:
                emp_commission=(obj.t_commission)/(len(obj.sale_rep))
            except:
                print"add atleast one  rep"
            rec=self.pool.get('commission.record')
            method_return=super(sale_order,self).action_wait(cr,uid,ids,context)
            for i in obj.sale_rep:
                rec.create(cr,uid,{'sale_date':obj.date_order,'sale_order':ids[0],'total_sale':obj.amount_total,'total_commission':obj.t_commission,'customer':obj.partner_id.id,'commission_employee':emp_commission,'state':'pending','commission_id':i.id},context)
     
        return method_return
    
    def action_cancel(self, cr, uid, ids, context=None):
         id=super(sale_order,self).action_cancel(cr,uid,ids,context)
         obj=self.pool.get('commission.record')
         cancel_id=obj.search(cr,uid,[('sale_order','=',ids)],context)
         obj.write(cr,uid,cancel_id,{'state':'cancel'},context)
         return id
         
            

    
class sale_order_line(osv.osv):
    _inherit='sale.order.line'
    _description='jjuice module'
    _columns={
               'commission':fields.float('Commission'),
              }
    
    def create(self, cr, uid, values, context=None):
        if context == None : context = {}
        if values.get('order_id') and values.get('product_id') and  any(f not in values for f in ['name', 'price_unit', 'type', 'product_uom_qty', 'product_uom']):
            order = self.pool['sale.order'].read(cr, uid, values['order_id'], ['pricelist_id', 'partner_id', 'date_order', 'fiscal_position'], context=context)
            defaults = self.product_id_change(cr, uid, [], order['pricelist_id'][0], values['product_id'],
                qty=float(values.get('product_uom_qty', False)),
                uom=values.get('product_uom', False),
                qty_uos=float(values.get('product_uos_qty', False)),
                uos=values.get('product_uos', False),
                name=values.get('name', False),
                partner_id=order['partner_id'][0],
                date_order=order['date_order'],
                fiscal_position=order['fiscal_position'][0] if order['fiscal_position'] else False,
                flag=False,  # Force name update
                context=context
            )['value']
            if context.get('price_unit_change',False):
                values['commission'] = self.price_unit_change(cr,uid,values.get('order_id',False),values.get('price_unit',False),values.get('product_id',False),defaults.get('product_uos_qty',False)).get('value',False).get('commission',False)
            if defaults.get('tax_id'):
                defaults['tax_id'] = [[6, 0, defaults['tax_id']]]
            values = dict(defaults, **values)
        return super(sale_order_line, self).create(cr, uid, values, context=context)

    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}
        lang = lang or context.get('lang', False)
        if not partner_id:
            raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
        warning = False
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        context = {'lang': lang, 'partner_id': partner_id,'price_unit_change':context.get('price_unit_change',False)}
        partner = partner_obj.browse(cr, uid, partner_id)
        lang = partner.lang
        context_partner = {'lang': lang, 'partner_id': partner_id}

        if not product:
            return {'value': {'th_weight': 0,
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)

        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False

        fpos = False
        if not fiscal_position:
            fpos = partner.property_account_position or False
        else:
            fpos = self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position)
        if update_tax: #The quantity only have changed
            result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)

        if not flag:
            result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
            if product_obj.description_sale:
                result['name'] += '\n'+product_obj.description_sale
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}
        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight        # Round the quantity up

        if not uom2:
            uom2 = product_obj.uom_id
        # get unit price

        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                    'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        })[pricelist]
            if price is False:
                warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist.")

                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                result.update({'price_unit': price})
        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        
        if product and not context.get('price_unit_change',False):
            result['commission']=self.price_unit_change(cr,uid,ids,result.get('price_unit',0),product,result.get('product_uos_qty',0),context)['value'].get('commission')
       
        return {'value': result, 'domain': domain, 'warning': warning} 
    
    def price_unit_change(self,cr,uid ,ids,price_unit,product_id,product_uos_qty,contex=None):
        res={'commission':0}
        product_object =self.pool.get('product.product').browse(cr,uid,product_id)
        price_standard = product_object.standard_price
        ir_model_data = self.pool.get('ir.model.data')
        volume_id = ir_model_data.get_object_reference(cr, uid, 'jjuice', 'attribute_vol')[1]
        for attribute in product_object.attribute_value_ids:
            if attribute.attribute_id.id == volume_id and price_unit > 0:
                total_commission=((price_unit-attribute.commission)/2)*product_uos_qty
                res['commission']=total_commission
                return {'value':res}
        return {'value':res}       
        
        
        
        


