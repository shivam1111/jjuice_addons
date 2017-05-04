from openerp import models, fields, api, _
from datetime import date
from openerp import SUPERUSER_ID

class res_users(models.Model):
    _inherit = "res.users"
    _description = "Users"
    
    @api.one
    def update_password(self,password):
        self.sudo().password = password
        return True

    @api.model
    def create_users(self,vals):
        res_partner = self.env['res.partner']
        country = self.env['res.country'].browse(eval(vals.get('country_id',False)))
        source_id = self.env.ref('account_acquisition.source_website')
        if country.code == "US":
            state_id = eval(vals.get('state_id',False))
        else:
            state_name = vals.get('state_id',False)
            state = self.env['res.country.state'].search([('name','ilike',state_name)])
            if not state:
                state = self.env['res.country.state'].create({
                        'name':state_name,
                        'code':"".join(e[0] for e in state_name.split()),
                        'country_id':country.id,
                    })
            state_id = state.id
        values = {
            'name':vals.get('name',''),
            'email':vals.get('email',''),
            'street':vals.get('street',''),
            'street2':vals.get('street2',''),
            'zip':vals.get('zip',''),
            'state_id':state_id,
            'phone':vals.get('phone',''),
            'acquisition_id':source_id and source_id.id or False,
            'country_id':eval(vals.get('country_id',False)),
            'vat':vals.get('vat',''),
            'city':vals.get('city',''),
            'classify_finance':'website',
            'customer':True,
            'leads':False,
        }

        partner = res_partner.create(values)
        user = self.env['res.users'].sudo()
        values.update({
            'partner_id': partner.id,
            'login':vals.get('email',''),
        })

        user._signup_create_user(values)
        user_id = self.search([('login','=',vals.get('email',''))])

        if user_id and vals.get('register-confirm-password',False):
            user_id.sudo().password = vals.get('register-confirm-password','')

        if vals.get('is_wholesale',False):
            partner.classify_finance = vals.get('type_account','website')
            partner.resale_no = vals.get('vat','')
            partner.customer = False
            partner.leads = True
            user_id.sudo().active = False
        template = self.env.ref('django_panel.email_template_registration_website', False)
        self.env['email.template'].sudo().browse(template.id).send_mail(partner.id,force_send=False)
        return user_id.id
    