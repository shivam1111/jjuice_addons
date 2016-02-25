from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class customer_filter_wizard(models.TransientModel):
    _name = "customer.filter.wizard"
    _description = "Customer filter wizard"
    
    def get_customer_type_of_account(self,cr,type_of_account):
        cr.execute('''
            select id from res_partner where acccount_type = '%s' and customer = true
        '''%(type_of_account))
        customer_list = cr.fetchall()
        return customer_list
    
    def get_customer_not_product_line(self,cr,attr):
        # This will return the list of customers who have order the product line with attributes id in attr
        attr_list = map(lambda x:x.id,attr)
        attr_list.append(0) # This is to avoid conversion of list with single element to tuple coz then the tuple is like (x,) and this format gives 
        #error in query
        attr_list = tuple(attr_list)
        cr.execute('''
            select invoice.partner_id from account_invoice_line as line left join account_invoice as invoice on line.invoice_id = invoice.id
                left join product_product as product on product.id   = line.product_id left join product_attribute_value_product_product_rel
                    as rel on rel.prod_id = product.id where rel.att_id in {0}
                    '''.format(attr_list))
        customer_list = cr.fetchall()
        return customer_list
    
    def get_customer_last_order_date(self,cr,last_order_date):
        # This method return the list of customers who have ordered after the given date
        cr.execute('''
            select partner_id from account_invoice where date_invoice >= '%s'
        '''%(last_order_date))
        customer_list  = cr.fetchall()
        return customer_list

    def get_all_customers(self,cr):
        cr.execute('''
            select id from res_partner where customer = true
        ''')
        customer_list = cr.fetchall()
        return customer_list

    def dummy_buttons(self,cr,uid,ids,context=None):
        return True
    
    def filter_customers(self,cr,uid,ids,context=None):
        assert len(ids) == 1
        total_customer_list = set(self.get_all_customers(cr))
        final_customer_list = set([])
        wizard = self.browse(cr,uid,ids[0],context)
        for index,i in enumerate(wizard.line_ids): # to check whether it is the first loop so that first loop will always be OR
            if i.field_type == 'last_order_date':
                customer_list = total_customer_list - set(self.get_customer_last_order_date(cr,i.last_order_date))
            elif i.field_type == "not_product_line":
                customer_list = total_customer_list - set(self.get_customer_not_product_line(cr,i.volume_attributes))
            elif i.field_type == "type_account":
                customer_list = set(self.get_customer_type_of_account(cr,i.type_of_account))
            if i.operator == 'or' or index == 0:
                final_customer_list = final_customer_list.union(customer_list)
            elif i.operator == 'and':
                final_customer_list = final_customer_list.intersection(customer_list)                
        final_customer_list = list(final_customer_list)
        list_customers = map(lambda x:x[0],final_customer_list) 
        return list_customers
    
    def _constraint_line_account(self,cr,uid,ids,context=None):
        for i in ids:
            cr.execute('''
                        select field_type from customer_filter_wizard_line where wizard_id = %s
                       '''%(i))
            type_list  = cr.fetchall()
            if len(type_list)!=len(set(type_list)):
                return False
            else:True
        return True
            
    _constraints = [
                    (_constraint_line_account,"No two constraint lines can have the same constraints",['line_ids'])
                    ]

    line_ids = fields.One2many('customer.filter.wizard.line','wizard_id','Add Constraints')

ACCOUNT_TYPE  = [('chain_store',"Chain Store(5+)"),('retailer','Retailer'),('private_label','Private Labeler'),
                 ('wholesale','Wholesale/Distribution'),('wholesaler','Wholesale & Retail'),
                 ('whitelabeling','Intrested in White Labeling'),('merchant','Merchant Processor'),
                 ('trade show','Trade Show Sales Rep'),('marketing','Marketing Rep'),
                 ('legal representative','Legal Representative For Eliquid Industry'),('website','Website(vapejjuice.com)'),
                 ('other','Other/Miscellaneous Account')
]
        
class customer_fitler_wizard_line(models.TransientModel):
    _name = "customer.filter.wizard.line"
    _description = "Customer Filter Wizard Line"
    
    wizard_id = fields.Many2one('customer.filter.wizard')
    operator = fields.Selection([
                                 ('and','AND'),('or','OR')
                                 ],string='Operator',default='or',required=True)
    field_type = fields.Selection([
                                   ('last_order_date','Last Order Date'),('type_account','Type of Account'),
                                   ('not_product_line','Does not have Product line')
                                   ],string = 'Constraint On',required=True)
    last_order_date = fields.Date('Last Order Date')
    type_of_account = fields.Selection(ACCOUNT_TYPE,'Type of Account')
    volume_attributes = fields.Many2many('product.attribute.value','customer_filter_line_attributes','line_id','attribute_id',string='Product Line')                              
    