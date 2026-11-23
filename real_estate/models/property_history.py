from odoo import fields, models


class PropertyHistory(models.Model):
    _name = "property.history"
    _description = "Property State History"
    _order = "create_date desc, id desc"

    user_id = fields.Many2one("res.users", readonly=True)
    property_id = fields.Many2one("property", ondelete="cascade", readonly=True)
    old_state = fields.Char(readonly=True)
    new_state = fields.Char(readonly=True)
    reason = fields.Char(readonly=True)
