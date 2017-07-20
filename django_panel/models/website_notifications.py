from openerp import models, fields, api, _
from helpers import BinaryS3Field, delete_object_bucket, get_bucket_location
from openerp.exceptions import except_orm


class website_notifications(models.Model):
    _name = "website.notifications"
    _description = "Website Notifications"
    _order = "sequence"

    sequence = fields.Integer('Sequence')
    name = fields.Text("Notification")
    active = fields.Boolean("Active")