from openerp.osv import fields, osv 
from openerp.tools.translate import _

class volume_price(osv.osv):
    _name = "volume.prices.line"
    _columns = {
                'customer_id':fields.many2one('res.partner','Customer',invisible=True),
                'product_attribute':fields.many2one('product.attribute.value',"Volume"),
                'price':fields.float("Price"),
                }
    
class res_partner_order(osv.osv):
    _inherit="res.partner"
    _description="jjuice"
    _defaults = {
                 'user_id':lambda self,cr,uid,context: uid
                 }
    def _check_customer_type(self, cr, uid, ids, context=None):
        for partner in self.browse(cr,uid,ids,context):
            if partner.customer and partner.leads:
                return False
        return True
                
    _constraints = [
        (_check_customer_type, 'Error: A Partner cannot be lead and a customer at the same time', ['customer','leads']),
        ]   

    def set_price(self,cr,uid,id,context=None):
        result = {}
        customer = self.pool.get('res.partner').browse(cr,uid,id,context)
        for i in customer.volume_prices:
            result.update({i.product_attribute.id:i.price})
        return result
    
    def call_view_jjuice(self,cr,uid,ids,context):
        return {
                'type':'ir.actions.client',
                'tag':'graph.action',
                'context':context,
                }
    _columns={
              "leads":fields.boolean("Lead"),
              "order":fields.one2many("res.partner.order","partners"),
              'volume_prices':fields.one2many('volume.prices.line','customer_id',"Prices"),             
              'email_multi_to':fields.one2many('multi.email','partner_id',"Addition Email IDs")
              }

class multi_email(osv.osv):
    _name = "multi.email"
    _columns = {
                'email':fields.char('Email'),
                'partner_id':fields.many2one('res.partner','Partner')
                }
    
class res_partner_orders(osv.osv):
        _name="res.partner.order"
        _description="partner module"
        _columns={
                    "partners":fields.many2one("res.partner","partner"),
                    "name":fields.char("Name"),
                    "order_date":fields.date("Order Date"),
                    "ref":fields.char("Ref"),
                    "res_partner":fields.many2one("res.partner","Customer"),
                    
                    #"product":fields.many2one("product.product","Product"),
                    "10_ml":fields.one2many("res.partner.ml","product_id","10 Ml"),
                    "350_ml":fields.one2many("res.partner.ml","product_id","350 Ml"),
                  }
        
class res_partner_ml(osv.osv):
    _name="res.partner.ml"
    _description="jjuice"
    _columns={
              "product_id":fields.many2one("product.product","Product"),
              "quantity":fields.float("Quantity"),
              "unit_price":fields.float("Unit Price"),
              "sub_total":fields.float("Sub Total"),
              }     
    
