import math
import re
import time
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import osv, fields, expression
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import psycopg2
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round, float_compare


class product_template(osv.osv):
    _inherit = "product.template"


    def _check_product_template_custom(self,cr,uid,ids,context=None):
        for product in self.browse(cr,uid,ids,context):
            if product.product_tmpl_id:
                return False
        return True
    
    def _get_default_sale_ok(self,cr,uid,context=None):
        if context.get('search_default_filter_to_sell',False):
            return True
        else: return False
    
    _defaults = {
                 'sale_ok':_get_default_sale_ok
                 }
#    _constraints = [
 #                   (_check_product_template_custom,'Error: Cannot change the name of the regular product\n To change its name change, the name of the custom product template\n',['name'])
  #                  ]
    _columns = {
                'product_tmpl_id':fields.many2one('product.template.custom'),
                'attribute_value_ids_custom': fields.many2many('product.attribute.value', id1='prod_id', id2='att_id', string='Attributes', readonly=True, ondelete='restrict'),
                }
 
 
    
class product_attribute_line_custom(osv.osv):
    _name = "product.attribute.line.custom"
    _rec_name = 'attribute_id'
    _columns = {
        'product_tmpl_id': fields.many2one('product.template.custom', 'Product Template', required=True, ondelete='cascade'),
        'attribute_id': fields.many2one('product.attribute', 'Attribute', required=True, ondelete='restrict'),
        'value_ids': fields.many2many('product.attribute.value', id1='line_id', id2='val_id', string='Product Attribute Value'),
    }


class product_template_custom(osv.osv):
    _name = "product.template.custom"
    _inherit = ['mail.thread']
    _description = "Product Template"
    _order = "name"

    def _check_top_fifteen(self, cr, uid, ids, context=None):
        cr.execute('''
            select count(*) from product_template_custom where top_fifteen = true
        ''')
        count = cr.fetchall()[0][0]
        if (count > 15):
            return False
        return True
    
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    def _product_template_price(self, cr, uid, ids, name, arg, context=None):
        plobj = self.pool.get('product.pricelist')
        res = {}
        quantity = context.get('quantity') or 1.0
        pricelist = context.get('pricelist', False)
        partner = context.get('partner', False)
        if pricelist:
            # Support context pricelists specified as display_name or ID for compatibility
            if isinstance(pricelist, basestring):
                pricelist_ids = plobj.name_search(
                    cr, uid, pricelist, operator='=', context=context, limit=1)
                pricelist = pricelist_ids[0][0] if pricelist_ids else pricelist
            if isinstance(pricelist, (int, long)):
                products = self.browse(cr, uid, ids, context=context)
                qtys = map(lambda x: (x, quantity, partner), products)
                pl = plobj.browse(cr, uid, pricelist, context=context)
                price = plobj._price_get_multi(cr,uid, pl, qtys, context=context)
                for id in ids:
                    res[id] = price.get(id, 0.0)
        for id in ids:
            res.setdefault(id, 0.0)
        return res

    def get_history_price(self, cr, uid, product_tmpl, company_id, date=None, context=None):
        if context is None:
            context = {}
        if date is None:
            date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        price_history_obj = self.pool.get('product.price.history')
        history_ids = price_history_obj.search(cr, uid, [('company_id', '=', company_id), ('product_template_id', '=', product_tmpl), ('datetime', '<=', date)], limit=1)
        if history_ids:
            return price_history_obj.read(cr, uid, history_ids[0], ['cost'], context=context)['cost']
        return 0.0

    def _set_standard_price(self, cr, uid, product_tmpl_id, value, context=None):
        ''' Store the standard price change in order to be able to retrieve the cost of a product template for a given date'''
        if context is None:
            context = {}
        price_history_obj = self.pool['product.price.history']
        user_company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        company_id = context.get('force_company', user_company)
        price_history_obj.create(cr, uid, {
            'product_template_id': product_tmpl_id,
            'cost': value,
            'company_id': company_id,
        }, context=context)

    def _get_product_variant_count(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for product in self.browse(cr, uid, ids):
            res[product.id] = len(product.product_variant_ids)
        return res

    _columns = {
        'name': fields.char('Name', required=True, translate=True, select=True),
        'taxes_id': fields.many2many('account.tax', 'product_taxes_rel',
            'prod_id', 'tax_id', 'Customer Taxes',
            domain=[('parent_id','=',False),('type_tax_use','in',['sale','all'])]),
        'supplier_taxes_id': fields.many2many('account.tax',
            'product_supplier_taxes_rel', 'prod_id', 'tax_id',
            'Supplier Taxes', domain=[('parent_id', '=', False),('type_tax_use','in',['purchase','all'])]),
        'property_account_income': fields.property(
            type='many2one',
            relation='account.account',
            string="Income Account",
            help="This account will be used for invoices instead of the default one to value sales for the current product."),
        'property_account_expense': fields.property(
            type='many2one',
            relation='account.account',
            string="Expense Account",
            help="This account will be used for invoices instead of the default one to value expenses for the current product."),
        
        'top_fifteen':fields.boolean("Top Fifteen"),        
        'product_manager': fields.many2one('res.users','Product Manager'),
        'description': fields.text('Description',translate=True,
            help="A precise description of the Product, used only for internal information purposes."),
        'description_purchase': fields.text('Purchase Description',translate=True,
            help="A description of the Product that you want to communicate to your suppliers. "
                 "This description will be copied to every Purchase Order, Receipt and Supplier Invoice/Refund."),
        'description_sale': fields.text('Sale Description',translate=True,
            help="A description of the Product that you want to communicate to your customers. "
                 "This description will be copied to every Sale Order, Delivery Order and Customer Invoice/Refund"),
        'type': fields.selection([('product','Stockable Product'),('consu', 'Consumable'),('service','Service')], 'Product Type', required=True, help="Consumable are product where you don't manage stock, a service is a non-material product provided by a company or an individual."),        
        'rental': fields.boolean('Can be Rent'),
        'categ_id': fields.many2one('product.category','Internal Category', required=True, change_default=True, domain="[('type','=','normal')]" ,help="Select category for the current product"),
        'price': fields.function(_product_template_price, type='float', string='Price', digits_compute=dp.get_precision('Product Price')),
        'list_price': fields.float('Sale Price', digits_compute=dp.get_precision('Product Price'), help="Base price to compute the customer price. Sometimes called the catalog price."),
        'lst_price' : fields.related('list_price', type="float", string='Public Price', digits_compute=dp.get_precision('Product Price')),
        'standard_price': fields.property(type = 'float', digits_compute=dp.get_precision('Product Price'), 
                                          help="Cost price of the product template used for standard stock valuation in accounting and used as a base price on purchase orders.", 
                                          groups="base.group_user", string="Cost Price"),
        'volume': fields.float('Volume', help="The volume in m3."),
        'weight': fields.float('Gross Weight', digits_compute=dp.get_precision('Stock Weight'), help="The gross weight in Kg."),
        'weight_net': fields.float('Net Weight', digits_compute=dp.get_precision('Stock Weight'), help="The net weight in Kg."),
        'warranty': fields.float('Warranty'),
        'sale_ok': fields.boolean('Can be Sold', help="Specify if the product can be selected in a sales order line."),
        'pricelist_id': fields.dummy(string='Pricelist', relation='product.pricelist', type='many2one'),
        'state': fields.selection([('',''),
            ('draft', 'In Development'),
            ('sellable','Normal'),
            ('end','End of Lifecycle'),
            ('obsolete','Obsolete')], 'Status'),
        'uom_id': fields.many2one('product.uom', 'Unit of Measure', required=True, help="Default Unit of Measure used for all stock operation."),
        'uom_po_id': fields.many2one('product.uom', 'Purchase Unit of Measure', required=True, help="Default Unit of Measure used for purchase orders. It must be in the same category than the default unit of measure."),
        'uos_id' : fields.many2one('product.uom', 'Unit of Sale',
            help='Specify a unit of measure here if invoicing is made in another unit of measure than inventory. Keep empty to use the default unit of measure.'),
        'uos_coeff': fields.float('Unit of Measure -> UOS Coeff', digits_compute= dp.get_precision('Product UoS'),
            help='Coefficient to convert default Unit of Measure to Unit of Sale\n'
            ' uos = uom * coeff'),
        'mes_type': fields.selection((('fixed', 'Fixed'), ('variable', 'Variable')), 'Measure Type'),
        'company_id': fields.many2one('res.company', 'Company', select=1),
        # image: all image fields are base64 encoded and PIL-supported
        'image': fields.binary("Image",
            help="This field holds the image used as image for the product, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image", 
            store={
                'product.template.custom': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized image of the product. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved, "\
                 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={
                'product.template.custom': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of the product. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
        'packaging_ids': fields.one2many(
            'product.packaging', 'product_tmpl_id', 'Logistical Units',
            help="Gives the different ways to package the same product. This has no impact on "
                 "the picking order and is mainly used if you use the EDI module."),
        'seller_ids': fields.one2many('product.supplierinfo', 'product_tmpl_id', 'Supplier'),
        'seller_delay': fields.related('seller_ids','delay', type='integer', string='Supplier Lead Time',
            help="This is the average delay in days between the purchase order confirmation and the receipts for this product and for the default supplier. It is used by the scheduler to order requests based on reordering delays."),
        'seller_qty': fields.related('seller_ids','qty', type='float', string='Supplier Quantity',
            help="This is minimum quantity to purchase from Main Supplier."),
        'seller_id': fields.related('seller_ids','name', type='many2one', relation='res.partner', string='Main Supplier',
            help="Main Supplier who has highest priority in Supplier List."),

        'active': fields.boolean('Active', help="If unchecked, it will allow you to hide the product without removing it."),
        'color': fields.integer('Color Index'),
        'attribute_line_ids': fields.one2many('product.attribute.line.custom', 'product_tmpl_id', 'Product Attributes'),
        'product_variant_ids': fields.one2many('product.template', 'product_tmpl_id', 'Products', required=True),
        'product_variant_count': fields.function( _get_product_variant_count, type='integer', string='# of Product Variants'),

        # related to display product product information if is_product_variant
        'ean13': fields.related('product_variant_ids', 'ean13', type='char', string='EAN13 Barcode'),
        'default_code': fields.related('product_variant_ids', 'default_code', type='char', string='Internal Reference'),
    }

    def _price_get_list_price(self, product):
        return 0.0

    def _price_get(self, cr, uid, products, ptype='list_price', context=None):
        if context is None:
            context = {}

        if 'currency_id' in context:
            pricetype_obj = self.pool.get('product.price.type')
            price_type_id = pricetype_obj.search(cr, uid, [('field','=',ptype)])[0]
            price_type_currency_id = pricetype_obj.browse(cr,uid,price_type_id).currency_id.id

        res = {}
        product_uom_obj = self.pool.get('product.uom')
        for product in products:
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost price for users not in this group
            # We fetch the standard price as the superuser
            if ptype != 'standard_price':
                res[product.id] = product[ptype] or 0.0
            else:
                company_id = product.env.user.company_id.id
                product = product.with_context(force_company=company_id)
                res[product.id] = res[product.id] = product.sudo()[ptype]
            if ptype == 'list_price':
                res[product.id] += product._name == "product.product" and product.price_extra or 0.0
            if 'uom' in context:
                uom = product.uom_id or product.uos_id
                res[product.id] = product_uom_obj._compute_price(cr, uid,
                        uom.id, res[product.id], context['uom'])
            # Convert from price_type currency to asked one
            if 'currency_id' in context:
                # Take the price_type currency from the product field
                # This is right cause a field cannot be in more than one currency
                res[product.id] = self.pool.get('res.currency').compute(cr, uid, price_type_currency_id,
                    context['currency_id'], res[product.id],context=context)

        return res

    def _get_uom_id(self, cr, uid, *args):
        return self.pool["product.uom"].search(cr, uid, [], limit=1, order='id')[0]

    def _default_category(self, cr, uid, context=None):
        if context is None:
            context = {}
        if 'categ_id' in context and context['categ_id']:
            return context['categ_id']
        md = self.pool.get('ir.model.data')
        res = False
        try:
            res = md.get_object_reference(cr, uid, 'product', 'product_category_all')[1]
        except ValueError:
            res = False
        return res

    def onchange_uom(self, cursor, user, ids, uom_id, uom_po_id):
        if uom_id:
            return {'value': {'uom_po_id': uom_id}}
        return {}

    def create_variant_ids(self, cr, uid, ids,vals=None, context=None):
        product_obj = self.pool.get("product.template")
        ctx = context and context.copy() or {}
        if ctx.get("create_product_variant"):
            return None

        ctx.update(active_test=False, create_product_variant=True)

        tmpl_ids = self.browse(cr, uid, ids, context=ctx)
        for tmpl_id in tmpl_ids:
            if vals == None:
                vals = self.read(cr,uid,tmpl_id.id,[],context)
                for i in vals:
                    if isinstance(vals.get(i,False),tuple):
                        vals[i] = vals.get(i,False)[0]
                vals.pop('write_uid',None)
                vals.pop('create_uid',None)
                vals.pop('attribute_line_ids',None)
                vals.pop('__last_update',None)
                vals.pop('product_variant_ids',None)
                vals.pop('product_variant_count',None)
                vals.pop('create_date',None)
                vals.pop('message_ids',None)
            else:
                vals.pop('attribute_line_ids',None)
            # list of values combination
            variant_alone = []
            all_variants = [[]]
            for variant_id in tmpl_id.attribute_line_ids:
                if len(variant_id.value_ids) == 1:
                    variant_alone.append(variant_id.value_ids[0])
                temp_variants = []
                for variant in all_variants:
                    for value_id in variant_id.value_ids:
                        temp_variants.append(variant + [int(value_id)])
                all_variants = temp_variants
            # adding an attribute with only one value should not recreate product
            # write this attribute on every product to make sure we don't lose them
            for variant_id in variant_alone:
                product_ids = []
                for product_id in tmpl_id.product_variant_ids:
                    if variant_id.id not in map(int, product_id.attribute_value_ids_custom):
                        product_ids.append(product_id.id)
                        vals.update({'attribute_value_ids_custom': [(4, variant_id.id)]})
                product_obj.write(cr, uid, product_ids, vals, context=ctx)
            # check product
            variant_ids_to_active = []
            variants_active_ids = []
            variants_inactive = []
            for product_id in tmpl_id.product_variant_ids:
                variants = map(int,product_id.attribute_value_ids_custom)
                if variants in all_variants:
                    variants_active_ids.append(product_id.id)
                    all_variants.pop(all_variants.index(variants))
                    if not product_id.active:
                        variant_ids_to_active.append(product_id.id)
                else:
                    variants_inactive.append(product_id)
            if variant_ids_to_active:
                product_obj.write(cr, uid, variant_ids_to_active, {'active': True}, context=ctx)
            # create new product
            for variant_ids in all_variants:
                if variant_ids:
                    cr.execute('''
                    select attribute_id from product_attribute_value where id in %s
                    ''',(tuple(variant_ids),))
                    l = cr.fetchall()
                vals.update({'attribute_value_ids_custom': [(6, 0, variant_ids)],'product_tmpl_id': tmpl_id.id,})                
                id = product_obj.create(cr, uid, vals, context=None)
                variants_active_ids.append(id)
                if variant_ids:
                    for attribute,variant in zip(l,variant_ids):
                        product_obj.write(cr,uid,id,{
                                              'attribute_line_ids':[
                                (0,0,{'attribute_id':attribute[0],'value_ids':[(6,0,[variant])]})
                                                                       ]
                                             },context=None)
            # unlink or inactive product
            for variant_id in map(int,variants_inactive):
                try:
                    with cr.savepoint():
                        product_obj.unlink(cr, uid, [variant_id], context=ctx)
                except (psycopg2.Error, osv.except_osv):
                    product_obj.write(cr, uid, [variant_id], {'active': False}, context=ctx)
                    pass
        return True

    def create(self, cr, uid, vals, context=None):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        product_template_id = super(product_template_custom, self).create(cr, uid, vals, context=context)
        if not context or "create_product_product" not in context:
            self.create_variant_ids(cr, uid, [product_template_id],vals, context=context)
 
        # TODO: this is needed to set given values to first variant after creation
        # these fields should be moved to product as lead to confusion
        related_vals = {}
        if vals.get('ean13'):
            related_vals['ean13'] = vals['ean13']
        if vals.get('default_code'):
            related_vals['default_code'] = vals['default_code']
        if related_vals:
            self.write(cr, uid, product_template_id, related_vals, context=context)
        return product_template_id

    def write(self, cr, uid, ids, vals, context=None):
        ''' Store the standard price change in order to be able to retrieve the cost of a product template for a given date'''
        if isinstance(ids, (int, long)):
            ids = [ids]
        for id in ids:
            if vals.get('name',False):
                cr.execute('''
                update product_template set name = '%s' where product_tmpl_id = %s
                ''' %(vals.get('name',False),id))
        if 'uom_po_id' in vals:
            new_uom = self.pool.get('product.uom').browse(cr, uid, vals['uom_po_id'], context=context)
            for product in self.browse(cr, uid, ids, context=context):
                 old_uom = product.uom_po_id
                 if old_uom.category_id.id != new_uom.category_id.id:
                     raise osv.except_osv(_('Unit of Measure categories Mismatch!'), _("New Unit of Measure '%s' must belong to same Unit of Measure category '%s' as of old Unit of Measure '%s'. If you need to change the unit of measure, you may deactivate this product from the 'Procurements' tab and create a new one.") % (new_uom.name, old_uom.category_id.name, old_uom.name,))
        res = super(product_template_custom, self).write(cr, uid, ids, vals, context=context)
        if 'attribute_line_ids' in vals or vals.get('active'):
             self.create_variant_ids(cr, uid, ids, context=context)
        if 'active' in vals and not vals.get('active'):
             ctx = context and context.copy() or {}
             ctx.update(active_test=False)
             product_ids = []
             for product in self.browse(cr, uid, ids, context=ctx):
                 product_ids = map(int,product.product_variant_ids)
             self.pool.get("product.product").write(cr, uid, product_ids, {'active': vals.get('active')}, context=ctx)
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        template = self.browse(cr, uid, id, context=context)
        default['name'] = _("%s (copy)") % (template['name'])
        return super(product_template_custom, self).copy(cr, uid, id, default=default, context=context)

    _defaults = {
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'product.template', context=c),
        'list_price': 1,
        'standard_price': 0.0,
        'sale_ok': 1,        
        'uom_id': _get_uom_id,
        'uom_po_id': _get_uom_id,
        'uos_coeff': 1.0,
        'mes_type': 'fixed',
        'categ_id' : _default_category,
        'type' : 'consu',
        'active': True,
    }

    def _check_uom(self, cursor, user, ids, context=None):
        for product in self.browse(cursor, user, ids, context=context):
            if product.uom_id.category_id.id != product.uom_po_id.category_id.id:
                return False
        return True

    def _check_uos(self, cursor, user, ids, context=None):
        for product in self.browse(cursor, user, ids, context=context):
            if product.uos_id \
                    and product.uos_id.category_id.id \
                    == product.uom_id.category_id.id:
                return False
        return True

    _constraints = [
        (_check_uom, 'Error: The default Unit of Measure and the purchase Unit of Measure must be in the same category.', ['uom_id']),
        (_check_top_fifteen, 'The Top Fifteen Limit has Exceeded', ['top_fifteen']),
    ]

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if 'partner_id' in context:
            pass
        return super(product_template_custom, self).name_get(cr, user, ids, context)
