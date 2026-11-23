from odoo import fields, models


class PropertyLine(models.Model):
    _name = "property.line"
    _description = "Property Room Line"

    property_id = fields.Many2one("property", ondelete="cascade")
    area = fields.Float()
    description = fields.Char()
