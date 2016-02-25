from openerp.osv import fields, osv
from openerp import models, fields, api,_

class account_voucher(osv.osv):
    _inherit='account.voucher'
    
    def button_proforma_voucher(self,cr,uid,ids,context=None):
        print '======================voucher',context
        if context is None:
            context={}
        invoice_obj=self.pool.get('account.invoice')
        ids_invoice=context.get('active_ids',[])
        super(account_voucher,self).button_proforma_voucher(cr,uid,ids,context)
        return invoice_obj.action_invoice_sent(cr,uid,ids_invoice,context)
        
class account_invoice(osv.osv):
    _inherit='account.invoice'
    
    def action_invoice_sent(self,cr,uid,ids,context=None):
        print '==========================send mail',context,ids,self
        context={}
        return super(account_invoice,self).action_invoice_sent(cr,uid,ids,context)