/** @odoo-module **/

import {Component, useState} from "@odoo/owl";
import {rpc} from "@web/core/network/rpc";
import {registry} from "@web/core/registry";

export class TogglePurchased extends Component {
    static template = "website_supermarket_list.TogglePurchased";
    static props = {
        listId: Number,
        lineId: Number,
        initialChecked: {type: Boolean, optional: true},
        disabled: {type: Boolean, optional: true},
    };

    setup() {
        this.state = useState({
            isChecked: this.props.initialChecked || false,
            isUpdating: false,
        });
    }

    async onChange(ev) {
        const isChecked = ev.target.checked;
        this.state.isUpdating = true;
        ev.target.disabled = true;

        try {
            const data = await rpc(
                `/my/grocery-lists/${this.props.listId}/toggle-purchased`,
                {
                    list_id: this.props.listId,
                    line_id: this.props.lineId,
                }
            );

            if (data.success) {
                this.state.isChecked = data.is_purchased;
                // Emit event to update progress bar and complete button
                const event = new CustomEvent("grocery_list_progress_updated", {
                    detail: {
                        progress: data.progress,
                        purchasedItems: data.purchased_items,
                        totalItems: data.total_items,
                    },
                });
                document.dispatchEvent(event);
            } else {
                // Revert state
                this.state.isChecked = !isChecked;
                ev.target.checked = !isChecked;
            }
        } catch (error) {
            // Revert state
            this.state.isChecked = !isChecked;
            ev.target.checked = !isChecked;
            alert("Error updating product status");
            console.error("Error:", error);
        } finally {
            this.state.isUpdating = false;
            ev.target.disabled = false;
        }
    }
}

registry
    .category("public_components")
    .add("website_supermarket_list.TogglePurchased", TogglePurchased);
