from openerp import models, fields, api, _
from openerp.exceptions import except_orm

_RATING = [
        ('0','Very Bad'),
        ('1','Bad'),
        ('2', 'Normal'),
        ('3', 'Good'),
        ('4','Very Good')
    ] 


class flavor_reviews(models.Model):
    _name = "flavor.reviews"
    _description="Flavor Reviews"
    
    
    name = fields.Char('Name')
    email = fields.Char('Email ID')
    title = fields.Char('Title')
    description = fields.Text('Description')
    flavor_id = fields.Many2one('product.flavors',string = "Flavor")
    partner_id = fields.Many2one('res.partner','Customer')
    rating = fields.Selection(_RATING,string = "Rating")
    