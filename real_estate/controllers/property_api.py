import json

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request

CREATE_FIELDS = {
    "name", "description", "postcode", "bedrooms", "living_room", "facades",
    "garage", "garden", "garden_area", "garden_orientation",
    "expected_price", "date_availability", "expected_selling_date",
}
READ_FIELDS = ["ref", "name", "postcode", "bedrooms", "expected_price", "selling_price", "state"]


class PropertyApi(http.Controller):
    """Small REST API. Requires an authenticated Odoo session (auth="user")."""

    @staticmethod
    def _json(payload, status=200):
        return request.make_json_response(payload, status=status)

    @http.route("/v1/property", methods=["POST"], type="http", auth="user", csrf=False)
    def create_property(self):
        try:
            vals = json.loads(request.httprequest.data.decode() or "{}")
        except ValueError:
            return self._json({"error": "Request body is not valid JSON."}, 400)
        if not isinstance(vals, dict):
            return self._json({"error": "JSON body must be an object."}, 400)

        unknown = set(vals) - CREATE_FIELDS
        if unknown:
            return self._json({"error": "Unknown fields: %s" % ", ".join(sorted(unknown))}, 400)
        if vals.get("name") and request.env["property"].search_count([("name", "=", vals["name"])]):
            return self._json({"error": "A property with this name already exists."}, 409)

        try:
            record = request.env["property"].create(vals)
        except (UserError, ValueError) as exc:
            return self._json({"error": str(exc)}, 400)
        return self._json(
            {"id": record.id, "ref": record.ref, "message": "created successfully"}, 201
        )

    @http.route("/v1/property", methods=["GET"], type="http", auth="user")
    def list_properties(self):
        records = request.env["property"].search_read([], READ_FIELDS, limit=100)
        return self._json(records)

    @http.route("/v1/property/<int:property_id>", methods=["GET"], type="http", auth="user")
    def get_property(self, property_id):
        record = request.env["property"].browse(property_id)
        if not record.exists():
            return self._json({"error": "Property not found."}, 404)
        return self._json(record.read(READ_FIELDS)[0])
