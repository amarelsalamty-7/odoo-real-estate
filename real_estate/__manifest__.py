{
    "name": "Real Estate Management",
    "summary": "Manage properties, owners, buildings and sale workflow in Odoo 17",
    "description": """
Real Estate Management
======================
* Property catalogue with owners, tags, rooms and garden details
* Status workflow (Draft -> Pending -> Sold -> Closed) with a full audit history
* Wizard to re-open a closed property with a mandatory reason
* Daily cron that flags properties past their expected selling date
* QWeb PDF report, OWL client action and a small REST endpoint
* Link between sale orders / partners and properties
    """,
    "author": "Ammar Elsalamty",
    "website": "https://github.com/<your-username>/odoo-real-estate",
    "category": "Real Estate",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "application": True,
    "installable": True,
    "depends": ["base", "mail", "sale"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "data/cron.xml",
        "views/base_menu.xml",
        "views/property_views.xml",
        "views/owner_view.xml",
        "views/tag_view.xml",
        "views/building_view.xml",
        "views/property_history_view.xml",
        "views/sale_order.xml",
        "views/res_partner_view.xml",
        "wizard/change_state_wizard.xml",
        "reports/property_report.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "real_estate/static/src/css/property.css",
            "real_estate/static/src/components/listView/listView.css",
            "real_estate/static/src/components/listView/listView.js",
            "real_estate/static/src/components/listView/listView.xml",
        ],
        "web.report_assets_common": [
            "real_estate/static/src/css/font.css",
        ],
    },
}
