from odoo import api, fields, models
from odoo.exceptions import ValidationError

STATES = [
    ("draft", "Draft"),
    ("pending", "Pending"),
    ("sold", "Sold"),
    ("closed", "Closed"),
]


class Property(models.Model):
    _name = "property"
    _description = "Property"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    ref = fields.Char(default="New", readonly=True, copy=False)
    name = fields.Char(required=True, tracking=True)
    description = fields.Text(tracking=True)
    postcode = fields.Char(required=True)
    date_availability = fields.Date(tracking=True)
    expected_selling_date = fields.Date(tracking=True)
    is_late = fields.Boolean(readonly=True)
    expected_price = fields.Float(tracking=True)
    selling_price = fields.Float(tracking=True)
    diff = fields.Float(compute="_compute_diff", string="Difference")
    bedrooms = fields.Integer(required=True)
    living_room = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        [("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")]
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(STATES, default="draft", tracking=True)

    owner_id = fields.Many2one("owner")
    tag_ids = fields.Many2many("tag")
    owner_address = fields.Char(related="owner_id.address", readonly=False)
    owner_phone = fields.Char(related="owner_id.phone", readonly=False)
    line_ids = fields.One2many("property.line", "property_id")

    _sql_constraints = [
        ("unique_name", "unique(name)", "This property name already exists!"),
    ]

    # ------------------------------------------------------------------
    # Compute / onchange / constraints
    # ------------------------------------------------------------------
    @api.depends("expected_price", "selling_price")
    def _compute_diff(self):
        for rec in self:
            rec.diff = rec.expected_price - rec.selling_price

    @api.onchange("expected_price")
    def _onchange_expected_price(self):
        if self.expected_price < 0:
            return {
                "warning": {
                    "title": "Invalid price",
                    "message": "The expected price cannot be negative.",
                }
            }

    @api.onchange("garden")
    def _onchange_garden(self):
        if not self.garden:
            self.garden_area = 0
            self.garden_orientation = False

    @api.constrains("bedrooms")
    def _check_bedrooms_greater_zero(self):
        for rec in self:
            if rec.bedrooms <= 0:
                raise ValidationError("Please add a valid number of bedrooms!")

    @api.constrains("expected_price", "selling_price")
    def _check_prices(self):
        for rec in self:
            if rec.expected_price < 0 or rec.selling_price < 0:
                raise ValidationError("Prices cannot be negative.")

    # ------------------------------------------------------------------
    # ORM overrides
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("ref", "New") == "New":
                vals["ref"] = self.env["ir.sequence"].next_by_code("property_seq") or "New"
        return super().create(vals_list)

    # ------------------------------------------------------------------
    # State workflow
    # ------------------------------------------------------------------
    def _change_state(self, new_state, reason=None):
        for rec in self:
            rec.create_history_record(rec.state, new_state, reason)
            rec.state = new_state

    def action_draft(self):
        self._change_state("draft")

    def action_pending(self):
        self._change_state("pending")

    def action_sold(self):
        self._change_state("sold")

    def action_closed(self):
        self._change_state("closed")

    def create_history_record(self, old_state, new_state, reason=None):
        for rec in self:
            self.env["property.history"].create(
                {
                    "user_id": self.env.uid,
                    "property_id": rec.id,
                    "old_state": old_state,
                    "new_state": new_state,
                    "reason": reason or "",
                }
            )

    def action_open_change_state_wizard(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "real_estate.change_state_wizard_action"
        )
        action["context"] = {"default_property_id": self.id}
        return action

    # ------------------------------------------------------------------
    # Cron
    # ------------------------------------------------------------------
    @api.model
    def check_expected_selling_date(self):
        """Flag open properties whose expected selling date has passed."""
        today = fields.Date.today()
        open_props = self.search([("state", "in", ("draft", "pending"))])
        late = open_props.filtered(
            lambda p: p.expected_selling_date and p.expected_selling_date < today
        )
        late.filtered(lambda p: not p.is_late).write({"is_late": True})
        (open_props - late).filtered("is_late").write({"is_late": False})
