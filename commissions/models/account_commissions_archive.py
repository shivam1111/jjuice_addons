from openerp import models, fields, api, _
from openerp.exceptions import except_orm

class account_commissions_archive(models.Model):
    _name = "account.commissions.archive"
    _description = "Commissions Calculator Archive"
    _rec_name = "user"

    @api.one
    @api.depends(
        'user',
        'from_date',
        'to_date',
    )
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

    
    user= fields.Many2one('res.users',string = "Sales Person",required=True)
    from_date = fields.Date('From',required=True)
    to_date = fields.Date('To',required=True)
    date = fields.Date('Date',help = "Date of creation",default = fields.Date.today)
    commission_line_ids = fields.One2many('account.commission.line.archive','archive_id','Commission Lines')
    