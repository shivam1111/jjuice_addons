from openerp.osv import fields, osv 
from openerp import tools
from openerp.tools.translate import _

class crm_lead(osv.osv):
    _inherit = "crm.lead"
    
    def create_quotation(self,cr,uid,ids,context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        partner_id = self.read(cr,uid,ids[0],['partner_id'],context)
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'view_partner_form')
        if partner_id.get('partner_id',False):
            return {
               'name':_("Create Quotation for Lead"),
                'view_mode': 'form',
                'view_id': view_id,
                'view_type': 'form',
                'res_model': 'res.partner',
                'res_id':partner_id.get('partner_id',[0])[0],
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
                'context': {
                            "lead":True,
                            "crm_lead_id":ids,
                }
            }
        else:
            raise osv.except_osv(
                _('Error!'),
                _('Cannot create quotation for the without any partner defined.'))
            
                        
        
    def case_mark_won(self, cr, uid, ids, context=None):
        partner = self.pool.get('res.partner')
        partner_list = []
        for oppurtunity in self.browse(cr,uid,ids,context):
            if oppurtunity.partner_id:
                if oppurtunity.partner_id.is_company:
                    partner_list = partner_list + partner.search(cr, uid, [('id','child_of',oppurtunity.partner_id.id)], offset=0, limit=None, order=None, context=None, count=False)
                else:
                    parent_company = oppurtunity.partner_id
                    while True:
                        if parent_company.parent_id:
                            parent_company = parent_company.parent_id
                        else:
                            break
                    partner_list = partner_list + partner.search(cr, uid, [('id','child_of',parent_company.id)], offset=0, limit=None, order=None, context=None, count=False)
                partner.write(cr,uid,partner_list,{'customer':True,'leads':False},context)
        return super(crm_lead,self).case_mark_won(cr, uid, ids, context=None)
    
    def _lead_create_contact(self,cr, uid, lead, name, is_company, parent_id=False,context=None):
        partner = self.pool.get('res.partner')
        if context.get('create_lead',False):
            vals = {'name': name,
                'user_id': lead.user_id.id,
                'comment': lead.description,
                'section_id': lead.section_id.id or False,
                'parent_id': parent_id,
                'phone': lead.phone,
                'mobile': lead.mobile,
                'email': tools.email_split(lead.email_from) and tools.email_split(lead.email_from)[0] or False,
                'fax': lead.fax,
                'acccount_type':lead.account_type,
                'leads':True,
                'customer':False,
                'title': lead.title and lead.title.id or False,
                'function': lead.function,
                'street': lead.street,
                'street2': lead.street2,
                'zip': lead.zip,
                'city': lead.city,
                'country_id': lead.country_id and lead.country_id.id or False,
                'state_id': lead.state_id and lead.state_id.id or False,
                'is_company': is_company,
                'type': 'contact'
            }
        else:
            vals = {'name': name,
                'user_id': lead.user_id.id,
                'comment': lead.description,
                'section_id': lead.section_id.id or False,
                'parent_id': parent_id,
                'phone': lead.phone,
                'supplier':True,
                'customer':False,
                'mobile': lead.mobile,
                'acccount_type':lead.account_type,
                'email': tools.email_split(lead.email_from) and tools.email_split(lead.email_from)[0] or False,
                'fax': lead.fax,
                'title': lead.title and lead.title.id or False,
                'function': lead.function,
                'street': lead.street,
                'street2': lead.street2,
                'zip': lead.zip,
                'city': lead.city,
                'country_id': lead.country_id and lead.country_id.id or False,
                'state_id': lead.state_id and lead.state_id.id or False,
                'is_company': is_company,
                'type': 'contact'
            }
        partner = partner.create(cr, uid, vals, context=context)
        return partner            

             
class crm_lead2opportunity_partner_lead(osv.osv_memory):
    _inherit = 'crm.lead2opportunity.partner'
    _description = 'Lead To Opportunity Partner'
    
    def action_apply(self,cr,uid,ids,context=None):
        if context is None:
            context={}
        
        obj=self.pool.get('crm.lead2opportunity.partner')
        l=obj.browse(cr,uid,ids,context=None)
        context.update(
                       {'create_lead':l.create_lead}
                       )
        return super(crm_lead2opportunity_partner_lead,self).action_apply(cr,uid,ids,context)
    
    _columns = {
                "create_lead":fields.boolean("Create Lead"),
                }
