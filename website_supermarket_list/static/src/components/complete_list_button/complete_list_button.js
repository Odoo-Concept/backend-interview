/** @odoo-module **/

import {Component, onWillDestroy, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";

export class CompleteListButton extends Component {
    static template = "website_supermarket_list.CompleteListButton";
    static props = {
        listId: Number,
        initialPendingItems: {type: Number, optional: true},
        initialTotalItems: {type: Number, optional: true},
        mode: {type: String, optional: true},
    };

    setup() {
        this.csrfToken = odoo.csrf_token;

        this.state = useState({
            pendingItems: this.props.initialPendingItems || 0,
            totalItems: this.props.initialTotalItems || 0,
        });

        // Listen for progress updates from toggle purchased components
        const updateProgress = (ev) => {
            const data = ev.detail || {};
            const purchasedItems = data.purchasedItems || data.purchased_items || 0;
            const totalItems = data.totalItems || data.total_items || 0;
            this.state.pendingItems = totalItems - purchasedItems;
            this.state.totalItems = totalItems;
        };

        document.addEventListener("grocery_list_progress_updated", updateProgress);
        onWillDestroy(() => {
            document.removeEventListener(
                "grocery_list_progress_updated",
                updateProgress
            );
        });
    }

    get isDisabled() {
        return this.state.pendingItems > 0;
    }
}

registry
    .category("public_components")
    .add("website_supermarket_list.CompleteListButton", CompleteListButton);
