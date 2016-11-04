from openerp import models, fields, api, _

class account_commissions(models.Model):
    _name = "account.commissions"
    _description = "Commissions Calculator"

    @api.one
    @api.depends(
        'user',
        'from_date',
        'to_date',
    )
    
    def _compute_payments(self):
        payment_ids = []
        if self.user and self.from_date and self.to_date:
            self._cr.execute("""
                select
                    l.id
                from
                    account_move_line l
                    left join account_account a on (l.account_id = a.id)
                    left join account_move am on (am.id=l.move_id)
                    left join account_invoice as inv on (inv.move_id = am.id)
                    left join res_partner partner on (l.partner_id = partner.id)
                    left join res_users as us on (us.id = partner.user_id) 
                where l.state != 'draft'
                  and a.type = 'liquidity'
                  and l.date >= '%s'
                  and l.date <='%s'
                  and us.id = %s
            """%(self.from_date,self.to_date,self.user.id))
            res = self._cr.fetchall()
            if len(res) > 0:
                payment_ids = map(lambda x:x[0],res)
        self.payment_ids = payment_ids
    
    @api.one
    @api.depends(
        'user',
        'from_date',
        'to_date',
    )
    def _calculate_commission(self):
        balance = 0.00
        commission = 0.00
        for i in self.payment_ids:
            diff = i.debit - i.credit
            balance+=diff
        if balance > 0:
            self.commission = 0.1*balance

    user= fields.Many2one('res.users',string = "Sales Person",required=True)
    from_date = fields.Date('From',required=True)
    to_date = fields.Date('To',required=True)
    payment_ids = fields.Many2many('account.move.line', string='Payments',
        compute='_compute_payments') 
    commission = fields.Float('Commission',help = "Commission is calculated as x% of difference between\
                                                         total debit - total credit in the columns",compute="_calculate_commission")
    
    
    
    