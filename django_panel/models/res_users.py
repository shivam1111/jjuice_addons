from openerp import models, fields, api, _
from datetime import date
from openerp import SUPERUSER_ID

class res_users(models.Model):
    _inherit = "res.users"
    _description = "Users"
    
    @api.model
    def create_users(self,vals):
#         {'city': 'Mandi Gobindgarh', 'register-email': 'shivam1111@gmail.com', 'name': 'Shivam Goyal', 'zip': '147301', 
#          'street2': '', 'po_box': 'on', 'country_id': '105', 'phone': '9855070234', 'street': 'Shastri Nagar, Sector 3A', 
#          'register-password': 'a', 'register-confirm-password': 'a', 'state_id': 'adsafsdf', 'vat': '', 
#          'g-recaptcha-response': '03AOP2lf5wTXqxLZ4_zS6eBCpx1F7LhXX1TBwc3DjegLwJ3RgmTki75d3ciE01RBxt4a5osBvrq49wXbrqU5w_QjHotIlxQvH57AeEcYSyKr3kODrhF3737Q0mw5A6KeVRIFD5Jd1ex-FpHVuXnQlw2_zeuiRu2_Sao3SDdMv7EN4N7WhR03mPnD6M5lvjR2tuQB-hzBCPhK-wygufQ5ADJrb2cw5IuxTxFwgZgyQyHUMlgcn3wJV6PSPoNyc95UxxVPYSNGBYmkk10Ad8Tq2iY84LioyWgpSLz0_czDSeoMzMcFhm-HKmLQQor7FHrgKmsv2g6Jl_fK5sx2irvyqUyjo-4kildNRkHqTrOjH94-yfIH9Aqc_7Hm4'
#         } 
#    is_wholesale=True
# {u'city': u'Mandi Gobindgarh', u'register-email': u'shivam1111@gmail.com', u'name': u'Shivam Goyal', u'zip': u'147301', 
# u'is_wholesale': u'on', u'street2': u'', u'register-confirm-password': u'a', u'country_id': u'105', u'phone': u'9855070234',
#  u'street': u'Shastri Nagar, Sector 3A', u'vat': u'fsdfsdfds', u'po_box': u'on', u'type_account': u'retailer', 
# u'state_id': u'adsafsdf', u'register-password': u'a', u'g-recaptcha-response': u'03AOP2lf6nR9OkkbNSLzuTUDBKQD7_Ctw0L3B2qQ7bKaXGxlV1NjUt9r53s-5ecQT0WGf-g97bKjvvNRSuY0_6zNQuX9jEMhw2G54udVCHrGAMMyfIoJ4tvquRWvg1_VG9rOA7kNQf92Nwx0AegJu0vPnoLvzmHF9leN6MtnQs1mAbbuE-XBDJ0Jo9G1D9D7LZq1A8-cNmxkTbsvE-RMrbrn9Wl2UnibvX09CIJkygW0WFo6PhlXxpjaHyKql58kwhzkhFW0evI1QOAgiGrhufoYecedCIAHyP0eikP61lLvQRC5Sz6JoCFll6802oXW6dQ-t68hYvb7427wr5PUoNJa_XMA-ohSSpFOgfvXPh9as-lN4Tg9oJglo'}

        res_partner = self.env['res.partner']
        country = self.env['res.country'].browse(eval(vals.get('country_id',False)))
        if country.code == "US":
            state_id = eval(vals.get('state_id',False))
        else:
            name = vals.get('state_id',False)
            state = self.env['res.country.state'].create({
                    'name':name,
                    'code':"".join(e[0] for e in name.split()),
                    'country_id':country.id,
                })
            state_id = state.id
        values = {
            'name':vals.get('name',''),
            'login':vals.get('email',''),
            'email':vals.get('email',''),
            'street':vals.get('street',''),
            'street2':vals.get('street2',''),
            'zip':vals.get('zip',''),
            'state_id':state_id,
            'phone':vals.get('phone',''),
            'country_id':eval(vals.get('country_id',False)),
            'vat':vals.get('vat',''),
            'city':vals.get('city',''),
            'classify_finance':'website'
        }
        partner = res_partner.create(values)
        user = self.env['res.users'].sudo()
        vals.update({
            'partner_id': partner.id,
        })
        user._signup_create_user(values)
        user_id = self.search([('login','=',vals.get('email',''))])
        if user_id and vals.get('register-confirm-password',False):
            user_id.password = vals.get('register-confirm-password','')
        if vals.get('is_wholesale',False):
            partner.classify_finance = vals.get('type_account','website')
            partner.resale_no = vals.get('vat','')
            partner.lead = True
            user.active = False        
        return True
    