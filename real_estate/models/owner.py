from odoo import fields, models


class Owner(models.Model):
    _name = "owner"
    _description = "Property Owner"

    name = fields.Char(required=True)
    phone = fields.Char()
    address = fields.Char()
    property_ids = fields.One2many("property", "owner_id")
