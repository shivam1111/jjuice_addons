from openerp import models, fields, api, _
from openerp.exceptions import except_orm

class account_commission_line_archive(models.Model):
    _name = "account.commission.line.archive"
    _description = "Commissions Line Archive"

    @api.one
    @api.depends('move_line_id')
    def _calculate_commission(self):
        commission = 0.00
        credit_move_line_id = self.move_line_id
        user_id = self.archive_id.user
        remarks = []
        
        """ 
            The account_move_line will be credited to reduce the debtor balance and this same line will reconciled with the 
            move line that was created to debit the partner balance in the sale journal. We have to find that account.move that
            is attached to invoice recording the debtor and product sale a/c entry        
        """

        if credit_move_line_id and credit_move_line_id.reconcile_id:
            reconcile_id = credit_move_line_id.reconcile_id
            partner_id = credit_move_line_id.partner_id
            
            # Calculate commissions only if the invoice is completely paid. Hence it should be reconciled completely
            debit_move_line_id = self.env['account.move.line'].search([('reconcile_id','=',reconcile_id.id),('journal_id.type','=','sale')])
            invoice_id = self.env['account.invoice'].search([('move_id','=',debit_move_line_id.move_id.id)])
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
                                self.write({'first_invoice':True})
                                if partner_id.classify_finance == 'retailer':
                                    remarks.append(" - Retail Customer")
                                    # This means customer is a retail customer
                                    # For the first time 20% total commission. 12% - Sales Manager, 8% - Sales rep
                                    am_com = 0.12 * diff
                                    sp_com = 0.08 * diff
                                elif partner_id.classify_finance in  ['wholesale','private_label']:
                                    remarks.append(" - Wholesale/Private Label")
                                    # This means customer is a wholesale/private label 
                                    # For the first time 10% total commission. 12% - Sales Manager, 8% - Sales rep
                                    am_com = 0.06 * diff
                                    sp_com = 0.04 * diff
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
    
                            if user_id.id == account_manager.id:
                                commission+= am_com
                            if user_id.id == salesman.id:
                                commission +=  sp_com
                        else:
                            remarks.append(" - Customer classification not set")
                            
        self.write({'remarks':''.join(remarks)})
        self.commission = commission
        
    move_line_id = fields.Many2one('account.move.line','Journal Line')
    name = fields.Char(related = 'move_line_id.ref')
    commission = fields.Float('Commmission',compute="_calculate_commission")
    remarks = fields.Text('Remarks')
    date = fields.Date(related = 'move_line_id.date',string = "Date")
    debit = fields.Float(related = "move_line_id.debit")
    credit = fields.Float(related = "move_line_id.credit")
    partner_id = fields.Many2one('res.partner',related = 'move_line_id.partner_id',string = "Customer")
    archive_id = fields.Many2one('account.commissions.archive',ondelete = 'cascade',required=True)
    first_invoice = fields.Boolean('First Invoice')
    
    