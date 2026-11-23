from odoo import fields, models
from odoo.exceptions import UserError


class ChangeState(models.TransientModel):
    _name = "change.state"
    _description = "Change Property State"

    property_id = fields.Many2one("property", required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("pending", "Pending")], default="draft", required=True
    )
    reason = fields.Char(required=True)

    def action_confirm(self):
        self.ensure_one()
        if self.property_id.state != "closed":
            raise UserError("Only closed properties can be re-opened with this wizard.")
        self.property_id._change_state(self.state, self.reason)
        return {"type": "ir.actions.act_window_close"}
