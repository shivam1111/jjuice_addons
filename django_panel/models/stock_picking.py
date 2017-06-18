from openerp import models, fields, api, _

class stock_picking(models.Model):
    _inherit = "stock.picking"

    promotion_id = fields.Many2one('promotion.codes',string='Promotion Code')
    order_website_note = fields.Text(string = "Order Note")