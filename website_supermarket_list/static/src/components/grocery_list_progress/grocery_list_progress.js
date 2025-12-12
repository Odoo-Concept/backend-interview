/** @odoo-module **/

import {Component, onWillDestroy, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";

export class GroceryListProgress extends Component {
    static template = "website_supermarket_list.GroceryListProgress";
    static props = {
        listId: Number,
        initialProgress: {type: Number, optional: true},
        initialPurchasedItems: {type: Number, optional: true},
        initialTotalItems: {type: Number, optional: true},
    };

    setup() {
        this.state = useState({
            progress: this.props.initialProgress || 0,
            purchasedItems: this.props.initialPurchasedItems || 0,
            totalItems: this.props.initialTotalItems || 0,
        });

        // Listen for progress updates from toggle purchased components
        const updateProgress = (ev) => {
            const data = ev.detail || {};
            this.state.progress = data.progress || 0;
            this.state.purchasedItems =
                data.purchasedItems || data.purchased_items || 0;
            this.state.totalItems = data.totalItems || data.total_items || 0;
        };

        document.addEventListener("grocery_list_progress_updated", updateProgress);
        onWillDestroy(() => {
            document.removeEventListener(
                "grocery_list_progress_updated",
                updateProgress
            );
        });
    }
}

registry
    .category("public_components")
    .add("website_supermarket_list.GroceryListProgress", GroceryListProgress);
