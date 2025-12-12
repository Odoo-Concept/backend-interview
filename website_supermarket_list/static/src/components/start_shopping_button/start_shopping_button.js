/** @odoo-module **/

import {Component, onMounted, onWillDestroy, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";

export class StartShoppingButton extends Component {
    static template = "website_supermarket_list.StartShoppingButton";
    static props = {
        listId: Number,
        initialTotalItems: {type: Number, optional: true},
        mode: {type: String, optional: true},
    };

    setup() {
        this.csrfToken = odoo.csrf_token;

        this.state = useState({
            totalItems: this.props.initialTotalItems || 0,
            errorMessage: null,
        });

        // Listen for progress updates to update total items
        const updateTotalItems = (ev) => {
            const data = ev.detail || {};
            if (data.totalItems !== undefined || data.total_items !== undefined) {
                this.state.totalItems = data.totalItems || data.total_items || 0;
                // Clear error if items are added
                if (this.state.totalItems > 0 && this.state.errorMessage) {
                    this.state.errorMessage = null;
                }
            }
        };

        document.addEventListener("grocery_list_progress_updated", updateTotalItems);
        onWillDestroy(() => {
            document.removeEventListener(
                "grocery_list_progress_updated",
                updateTotalItems
            );
        });

        // Listen for URL error parameter
        onMounted(() => {
            const urlParams = new URLSearchParams(window.location.search);
            const error = urlParams.get("error");
            if (error) {
                this.state.errorMessage = decodeURIComponent(error);
                // Remove error from URL
                const newUrl =
                    window.location.pathname +
                    window.location.search
                        .replace(/[?&]error=[^&]*/, "")
                        .replace(/^&/, "?");
                window.history.replaceState({}, "", newUrl);
            }
        });
    }

    get isDisabled() {
        return this.state.totalItems === 0;
    }

    onSubmit(event) {
        if (this.isDisabled) {
            event.preventDefault();
            this.state.errorMessage =
                "Cannot start shopping with an empty list. Please add at least one product to the list first.";
            // Scroll to top to show error
            window.scrollTo({top: 0, behavior: "smooth"});
            return false;
        }
        return true;
    }

    dismissError() {
        this.state.errorMessage = null;
    }
}

registry
    .category("public_components")
    .add("website_supermarket_list.StartShoppingButton", StartShoppingButton);
