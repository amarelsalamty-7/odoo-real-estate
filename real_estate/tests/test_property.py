from psycopg2 import IntegrityError

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestProperty(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Property = cls.env["property"]
        cls.property_01 = cls.Property.create({
            "name": "Property 1000",
            "description": "Property 1000 description",
            "postcode": "1010",
            "date_availability": fields.Date.today(),
            "bedrooms": 10,
            "expected_price": 10000,
        })

    def test_01_property_values(self):
        self.assertRecordValues(self.property_01, [{
            "name": "Property 1000",
            "description": "Property 1000 description",
            "postcode": "1010",
            "date_availability": fields.Date.today(),
            "bedrooms": 10,
            "expected_price": 10000,
            "state": "draft",
        }])

    def test_02_reference_is_generated(self):
        self.assertTrue(self.property_01.ref.startswith("PRT"))
        self.assertNotEqual(self.property_01.ref, "New")

    def test_03_workflow_creates_history(self):
        self.property_01.action_pending()
        self.property_01.action_sold()
        self.property_01.action_closed()
        self.assertEqual(self.property_01.state, "closed")
        history = self.env["property.history"].search(
            [("property_id", "=", self.property_01.id)], order="id"
        )
        self.assertEqual(
            [(h.old_state, h.new_state) for h in history],
            [("draft", "pending"), ("pending", "sold"), ("sold", "closed")],
        )

    def test_04_bedrooms_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self.property_01.bedrooms = 0

    def test_05_prices_cannot_be_negative(self):
        with self.assertRaises(ValidationError):
            self.property_01.expected_price = -1

    def test_06_name_is_unique(self):
        with self.assertRaises(IntegrityError), mute_logger("odoo.sql_db"):
            self.Property.create({"name": "Property 1000", "postcode": "1", "bedrooms": 1})

    def test_07_diff_is_computed(self):
        self.property_01.selling_price = 9000
        self.assertEqual(self.property_01.diff, 1000)

    def test_08_cron_flags_late_properties(self):
        self.property_01.expected_selling_date = fields.Date.subtract(fields.Date.today(), days=3)
        self.Property.check_expected_selling_date()
        self.assertTrue(self.property_01.is_late)
        self.property_01.expected_selling_date = fields.Date.add(fields.Date.today(), days=3)
        self.Property.check_expected_selling_date()
        self.assertFalse(self.property_01.is_late)

    def test_09_wizard_reopens_closed_property(self):
        self.property_01.action_closed()
        wizard = self.env["change.state"].create({
            "property_id": self.property_01.id,
            "state": "pending",
            "reason": "Buyer withdrew",
        })
        wizard.action_confirm()
        self.assertEqual(self.property_01.state, "pending")
        last = self.env["property.history"].search(
            [("property_id", "=", self.property_01.id)], order="id desc", limit=1
        )
        self.assertEqual(last.reason, "Buyer withdrew")

    def test_10_wizard_rejects_non_closed_property(self):
        wizard = self.env["change.state"].create({
            "property_id": self.property_01.id,
            "state": "pending",
            "reason": "n/a",
        })
        with self.assertRaises(UserError):
            wizard.action_confirm()
