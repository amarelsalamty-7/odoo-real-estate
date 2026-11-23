from odoo import fields, models


class Tag(models.Model):
    _name = "tag"
    _description = "Property Tag"

    name = fields.Char(required=True)
