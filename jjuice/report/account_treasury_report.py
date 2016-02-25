from openerp import tools
from openerp.osv import fields,osv

class account_treasury_report(osv.osv):
    _inherit = "account.treasury.report"
    _description = "Treasury Analysis"
    _auto = False
    
    _columns = {
                'partner_id':fields.many2one('res.partner','Partner',readonly=True),
                'account_type':fields.char("Account Type",readonly=True),
                }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'account_treasury_report')
        cr.execute("""
            create or replace view account_treasury_report as (
            select
                p.id as id,
                p.fiscalyear_id as fiscalyear_id,
                p.id as period_id,
                COALESCE (partner.acccount_type, 'No Label') as account_type ,
                l.partner_id as partner_id,
                sum(l.debit) as debit,
                sum(l.credit) as credit,
                sum(l.debit-l.credit) as balance,
                p.date_start as date,
                am.company_id as company_id
            from
                account_move_line l
                left join account_account a on (l.account_id = a.id)
                left join account_move am on (am.id=l.move_id)
                left join account_period p on (am.period_id=p.id)
                left join res_partner partner on (l.partner_id = partner.id)
            where l.state != 'draft'
              and a.type = 'liquidity'
            group by p.id, p.fiscalyear_id, p.date_start, am.company_id,l.partner_id,partner.acccount_type
            )
        """)

    