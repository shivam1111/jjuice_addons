from openerp.osv import fields, osv
from openerp import SUPERUSER_ID

class commission_employee(osv.osv):
    _name='commission.employee'
    _description='commission module'
    
    def commission_cal(self, cr, SUPERUSER_ID, ids, field_name, arg, context):
         res={}
         uid = SUPERUSER_ID
         if field_name=='pending_commission':
             for i in ids:
                 obj=self.browse(cr,uid,i).pending
                 sum=0
                 for j in obj:
                     sum=sum + j.commission_employee
                 res[i]=sum
             return res
         if field_name=='paid_commission':
             for i in ids:
                 obj=self.browse(cr,uid,i).paid
                 sum=0
                 for j in obj:
                     sum=sum + j.commission_employee
                 res[i]=sum
             return res
     
      
    _columns={
              'name':fields.many2one('hr.employee','Name',required=True),
              'pending_commission':fields.function(commission_cal,type='float',string='Pending Commission'),
              'paid_commission':fields.function(commission_cal,type='float',string='Paid Commission'),
              'pending':fields.one2many('commission.record','commission_id','Pending',domain = [('state','=','pending')]),
              'paid':fields.one2many('commission.record','commission_id','Paid',domain = [('state','=','paid')]),
              'cancel':fields.one2many('commission.record','commission_id','Paid',domain = [('state','=','cancel')]),
              'active':fields.boolean('Active'),
            }
    _defaults={'active':True,
               }
    def pay_all(self,cr,uid,id,context):
        obj=self.browse(cr,uid,id).pending
        print "obj",obj
        for i in obj:
            self.pool.get("commission.record").write(cr, uid, i.id, {'state':'paid'}, context=None)
            print" i am in loop"
        return True
    
    
        
    
    
class commission_record(osv.osv):
    _name='commission.record'
    _description='commission record'
    _columns={
              'sale_date':fields.date('Sale Date'),
              'total_sale':fields.float('Total Sale'),
              'total_commission':fields.float('Total Commission'),
              'customer':fields.many2one('res.partner','Customer'),
              'commission_employee':fields.float('Employee Commission'),
              'commission_id':fields.many2one('commission.employee','Commission'),
              'state':fields.selection([('pending','Pending'),('paid','Paid'),('cancel','Cancel')],'state'),
              'sale_order':fields.many2one('sale.order','Ref'),
              #'cal_commission':fields.function(commission_cal,type='float',string='Expected Re',track_visibility='always'), 
              }
    _defaults={'state':'pending',
               }
    
    def change_state(self,cr,uid,id,context):
        self.write( cr, uid, id, {'state':'paid'}, context=None)
        return True
    
           
           
            