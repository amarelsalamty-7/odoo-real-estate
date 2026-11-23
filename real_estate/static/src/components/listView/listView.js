/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class ListViewAction extends Component {
    static template = "real_estate.ListView";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({ records: [], loading: false });
        onWillStart(() => this.loadRecords());
    }

    async loadRecords() {
        this.state.loading = true;
        try {
            this.state.records = await this.orm.searchRead(
                "property",
                [],
                ["name", "postcode", "date_availability", "state"],
                { order: "id desc" }
            );
        } finally {
            this.state.loading = false;
        }
    }

    async createRecord() {
        const suffix = Date.now().toString().slice(-6);
        await this.orm.create("property", [
            {
                name: `New property ${suffix}`,
                postcode: "00000",
                bedrooms: 1,
                date_availability: new Date().toISOString().slice(0, 10),
            },
        ]);
        this.notification.add("Property created", { type: "success" });
        await this.loadRecords();
    }

    async deleteRecord(recordId) {
        await this.orm.unlink("property", [recordId]);
        this.notification.add("Property deleted", { type: "warning" });
        await this.loadRecords();
    }
}

registry.category("actions").add("real_estate.action_list_view", ListViewAction);
