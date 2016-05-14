from openerp import models, fields, api,_
import openerp.addons.decimal_precision as dp

_list_tab_style = [
                   (1,"Flavor Concentration Matrix"),
                   (2,"Products List"),
                   (3,"Marketing"),
                   (4,"Free Samples List"),
                   (5,"Free Samples Matrix"),
                ]

_type_of_product = [
                     ('consu','Consumable Product'),
                     ('product','Stockable Product'),
                     ]

class product_tab(models.Model):
    _name = "product.tab"
    _description = "Product Tab"
    _order = "sequence asc"
    
    @api.model
    def _get_attribute_domain(self):
        # We have access to self.env in this context.
        ids = self.env.ref('jjuice.attribute_vol').id
        return [('attribute_id','=', ids)]
    
    
    @api.model  
    def _create_product(self,pairs):
        #(tab_id,flavor_id,vol_id,conc_id) ---> pair
        product_obj = self.env['product.product']
        product_ids = []
        for pair in pairs:
            vals = {
                    'tab_id':pair[0],
                    'flavor_id': pair[1].id,
                    'vol_id':pair[2],
                    'conc_id':pair[3],
                    'type':self.consumable_stockable,
                    'name':pair[1].name,
                    'sale_ok':True,
                    'purchase_ok':True,
                
                }
            product_id = product_obj.create(vals)
            product_ids.append(product_id)
        return product_ids
    
    @api.model
    def _delete_product(self,pairs):
        #(tab_id,flavor_id,vol_id,conc_id) ---> pair
        product_obj = self.env['product.product']
        for pair in pairs:
            product_ids = product_obj.search([('tab_id','=',pair[0]),('flavor_id','=',pair[1].id),
                                ('vol_id','=',pair[2]),('conc_id','=',pair[3])])
            print "***********************product_ids",product_ids
            if product_ids:
                product_ids.unlink()
        return True
    
    @api.model
    def _create_pair_products(self,existing_pairs = [],new_pairs = []):
        '''
            * First check if existing pair are equal to new pairs. If yes then just do not do anything.
                If they are not equal then do the following.
                1. First find out the intersection (These pair will be kept as it is and not touched
                2. E - N will give us set of all the pairs that have been deleted
                3. N - E will give all set of the pairs that have to be created
            
            * the pairs will be list of tuple and the tuple will have the elements in position as follows (tab_id,flavor_id,vol_id,conc_id)  
        '''
        e_minus_n = set(existing_pairs) - set(new_pairs)
        n_minus_e = set(new_pairs) - set(existing_pairs)
        created_product_ids = []
        if e_minus_n:
            print "=============================we need to delete products",e_minus_n
            self._delete_product(e_minus_n)
        if n_minus_e:
            print "=============================we need to create products",n_minus_e
            created_product_ids.append(self._create_product(n_minus_e))
        print "////////////////////////////////////////////////e_minus_n",e_minus_n
        print "////////////////////////////////////////////////n_minus_e",n_minus_e
        return True
        
    @api.model
    def create(self,vals):
        result =  super(product_tab,self).create(vals)
        if (result.tab_style == 1 or result.tab_style == 5) and result.flavor_conc_line :
            new_pairs = result._create_pair()
            result._create_pair_products(new_pairs = new_pairs)
        return result
    
    @api.model
    def _create_pair(self):
        pairs = []
        for line in self.flavor_conc_line:
            tab_id,flavor_id,vol_id = line.tab_id.id,line.flavor_id,line.tab_id.vol_id.id 
            for conc in line.conc_ids:
                pairs.append((tab_id,flavor_id,vol_id,conc.id))
        return pairs        
        
    @api.multi
    def write(self,vals):
        # The list will contain tuples with the following position
        # 0:tab_id,1:(flavor_id,flavor name),2:vol_id,3:conc_id
        if vals.get('flavor_conc_line',False):    
            existing_pairs,new_pairs = [],[]
            existing_pairs = self._create_pair()
            result =  super(product_tab,self).write(vals)
            new_pairs = self._create_pair()
            self._create_pair_products(existing_pairs,new_pairs)
        else:
            result =  super(product_tab,self).write(vals)
        return result
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)',
            'Name of a tab must be unique!'),
        ('prod_uniq', 'unique(name)',
            'Tab,Volume,Concentration,Flavor. This combination should be unique!'),                        
                        
    ]    
    
    name = fields.Char('Tab Name',size=30,required=True)
    visible_all_customers = fields.Boolean("Visible to all Customers")
    specific_customer_ids = fields.Many2many('res.partner','product_tab_res_partners','tab_id','partner_id',string = "Customers",help = "List of Customer to whom this tab will be available to")
    tab_style = fields.Selection(_list_tab_style,string = "Tab Style",required=True,help = "These are options available that will format and determine the functionality of tab")
    product_ids = fields.One2many('product.product','tab_id','Products',help = "List of products belonging to this tab")
    vol_id = fields.Many2one('product.attribute.value',"Volume" ,domain = _get_attribute_domain)
    consumable_stockable = fields.Selection(_type_of_product,"Type of Product",required=True)
    sequence = fields.Integer('Sequence')
    active = fields.Boolean("Active",default=True)
    flavor_conc_line = fields.One2many(
                                        'flavor.conc.details','tab_id',"Flavors & Concentration Details"
                                        )
    input_width = fields.Char("Width",required=True,default="50px")
    
class flavor_concentration_details(models.Model):
    _name = "flavor.conc.details"
    _description = "flavor and Concentration detail for tabs"
    
    @api.model
    def create(self,vals):
        return super(flavor_concentration_details,self).create(vals)
    
    @api.model
    def _get_attribute_domain(self):
        # We have access to self.env in this context.
        ids = self.env.ref('jjuice.attribute_conc').id
        return [('attribute_id','=', ids)]    
    
    tab_id = fields.Many2one('product.tab','Tabs',ondelete='cascade', select=True)
    flavor_id = fields.Many2one('product.flavors','Flavor')
    conc_ids = fields.Many2many('product.attribute.value','details_conc','detail_id','conc_id','Concentrations',domain = _get_attribute_domain)
     