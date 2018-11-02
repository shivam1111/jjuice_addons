from openerp import models, fields, api, _
from openerp.exceptions import except_orm

class account_commission_line(models.Model):
    _name = "account.commission.line"
    _description = "Commissions Line"

    move_line = fields.Char('Journal Line')
    date = fields.Date("Date")
    commission = fields.Float('Commission')
    archive_id = fields.Many2one('account.commissions')
    remarks = fields.Text('Remarks')
    debit = fields.Float('Debit')
    credit = fields.Float('Credit')
    partner_id = fields.Many2one('res.partner',string = "Customer")
    first_invoice = fields.Boolean('First Invoice')
    invoice_id = fields.Many2one('account.invoice','Invoice')

class account_commissions(models.Model):
    _name = "account.commissions"
    _description = "Commissions Calculator"

    @api.one
    def name_get(self):
        name = self.user.name + "(" + self.from_date + "/" + self.to_date + ")" 
        return (self.id,name)
        
    def _calculate_commission(self,move_line,invoice_id):
        commission = 0.00
        credit_move_line_id = move_line
        user_id = self.user
        remarks = []
        res = {
        }
        """ 
            The account_move_line will be credited to reduce the debtor balance and this same line will reconciled with the 
            move line that was created to debit the partner balance in the sale journal. We have to find that account.move that
            is attached to invoice recording the debtor and product sale a/c entry        
        """

        partner_id = credit_move_line_id.partner_id
        if invoice_id:
            # Calculate commissions only if you know the invoice to which the payment is attached
            diff = credit_move_line_id.credit - credit_move_line_id.debit
            first_invoice = None
            invoices = partner_id.invoice_ids.filtered(lambda r: r.state == 'paid')
            account_manager = partner_id.user_id
            salesman = invoice_id.user_id
            remarks.append("%s input order"%(salesman.name))
            if invoices:                
                am_com = 0.00
                sp_com = 0.00
                # continue only once we are sure that we have the fist invoice id of this partner
                first_invoice = invoices.sorted(key = lambda r:r.id)[0]
                if diff > 0:
                    if partner_id.classify_finance:
                        if invoice_id.id == first_invoice.id:
                            remarks.append(" - First Invoice")
                            # This is the first invoice of the customer
                            res.update({'first_invoice':True})
                            if partner_id.classify_finance == 'retailer':
                                remarks.append(" - Retail Customer")
                                # This means customer is a retail customer
                                # For the first time 20% total commission. 12% - Sales Manager, 8% - Sales rep
                                am_com = 0.12 * diff
                                sp_com = 0.08 * diff
                            elif partner_id.classify_finance in  ['wholesale','private_label']:
                                remarks.append(" - Wholesale/Private Label")
                                # This means customer is a wholesale/private label 
                                # For the first time 10% total commission. 6% - Sales Manager, 4% - Sales rep
                                am_com = 0.06 * diff
                                sp_com = 0.04 * diff
                            elif partner_id.classify_finance == 'master_distributor':
                                remarks.append (" - Master Distributor")
                                # This means customer is a Master Distributor 
                                # For the first time 3% total commission. 1.5% - Sales Manager, 1.5% - Sales rep
                                am_com = 0.015 * diff
                                sp_com = 0.015 * diff                                   
                        else:
                            remarks.append(" - Repeat Customer")
                            # This is not the  first invoice of the customer
                            if partner_id.classify_finance == 'retailer':
                                remarks.append(" - Retail Customer")
                                # This means customer is a retail customer
                                # 10% total commission. 6% - Sales Manager, 4% - Sales rep
                                am_com = 0.06 * diff
                                sp_com = 0.04 * diff                            
                            elif partner_id.classify_finance in  ['wholesale','private_label']:
                                remarks.append(" - Wholesale/Private Label")
                                # This means customer is a wholesale/private label 
                                # 5% total commission. 3% - Sales Manager, 2% - Sales rep
                                am_com = 0.03 * diff
                                sp_com = 0.02 * diff
                            elif partner_id.classify_finance == 'master_distributor':
                                remarks.append (" - Master Distributor")
                                # This means customer is a Master Distributor 
                                # For the first time 1.5% total commission. 1% - Sales Manager, 0.5% - Sales rep
                                am_com = 0.010 * diff
                                sp_com = 0.005 * diff                                                                       
                                
                        if user_id.id == account_manager.id:
                            commission = commission + am_com
                        if user_id.id == salesman.id:
                            commission = commission + sp_com
                    else:
                        remarks.append("* Customer classification not set")
        res.update({
            'remarks':'\n'.join(remarks),
            'commission':commission
            })
        return res
    
    @api.constrains(
        'user',
        'from_date',
        'to_date',        
    )
    def check_date_archive(self):
        # check that to date always greater than from date
        # check always that for a particular employee the archives to date always less than from date
        if self.to_date <= self.from_date:
            raise except_orm("Error!","Sorry! To date should always be greater than from date")
        ids = self.search([('user','=',self.user.id),('from_date','<=',self.to_date),
                           ('to_date','>=',self.from_date),('id','!=',self.id)])
        if ids:
            raise except_orm("Error!","Sorry! Commissions dates overlapping for this Sales Person")    


    @api.multi
    def generate_archive(self):
        
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.commissions',
            'target': 'current',
            'res_id':self.id,
        }
            
    
    @api.one
    @api.onchange(
        'user',
        'from_date',
        'to_date',
    )    
    def compute_comission_lines(self):
        payment_ids = []
        if self.user and self.from_date and self.to_date:
            self._cr.execute("""
                select
                    l.id
                from
                    account_move_line l
                    left join account_account a on (l.account_id = a.id)
                    left join account_journal as aj on (l.journal_id = aj.id)
                    left join res_partner partner on (l.partner_id = partner.id)
                where l.state != 'draft'
                  and a.type = 'receivable'
                  and l.date >= '%s'
                  and l.date <='%s'
                  and aj.type in ('cash','bank')
                  and l.reconcile_id is not null
                  and (l.credit - l.debit) > 0
            """%(self.from_date,self.to_date))
            res = self._cr.fetchall()
            commission_lines = []
            if len(res) > 0:
                commission_line_ids = map(lambda x:x[0],res)
                for l in self.env['account.move.line'].browse(commission_line_ids):
                    if l.reconcile_id:
                        reconcile_id = l.reconcile_id
                        partner_id = l.partner_id
                        # Calculate commissions only if the invoice is completely paid. Hence it should be reconciled completely
                        debit_move_line_id = self.env['account.move.line'].search([('reconcile_id','=',reconcile_id.id),('journal_id.type','=','sale')])
                        invoice_id = self.env['account.invoice'].search([('move_id','=',debit_move_line_id.move_id.id)])
                        if invoice_id:  
                            account_manager = partner_id.user_id
                            salesman = invoice_id.user_id  
                            if self.user.id in [account_manager.id,salesman.id]:
                                res = self._calculate_commission(l,invoice_id)
                                commission_lines.append((0,0,{
                                                              'invoice_id':invoice_id.id,
                                                              'remarks':res.get('remarks',''),
                                                              'commission':res.get('commission',0),
                                                              'debit':l.debit,
                                                              'credit':l.credit,
                                                              'partner_id':l.partner_id,
                                                              'date':l.date,
                                                              'move_line':l.name_get()[0][1],
                                                          })) 
                self.commission_line_ids = commission_lines
    
    user= fields.Many2one('res.users',string = "Sales Person",required=True)
    from_date = fields.Date('From',required=True)
    to_date = fields.Date('To',required=True)
    commission_line_ids = fields.One2many('account.commission.line', 'archive_id',string='Payments')
                                          

