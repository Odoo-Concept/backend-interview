/** @odoo-module **/

import {Component, onMounted, onWillUnmount, useRef} from "@odoo/owl";
import {initStoreAutocomplete} from "@website_supermarket_list/js/store_autocomplete_init";
import {registry} from "@web/core/registry";

export class StoreAutocompleteComponent extends Component {
    static template = "website_supermarket_list.StoreAutocompleteComponent";
    static props = {};

    setup() {
        this.inputRef = useRef("input");
        this.storeAutocompleteCleanup = null;

        onMounted(() => {
            if (this.inputRef.el) {
                try {
                    this.storeAutocompleteCleanup = initStoreAutocomplete(
                        this.inputRef.el
                    );
                } catch (error) {
                    console.error("Error initializing store autocomplete:", error);
                }
            }
        });

        onWillUnmount(() => {
            if (this.storeAutocompleteCleanup) {
                this.storeAutocompleteCleanup();
            }
        });
    }
}

registry
    .category("public_components")
    .add(
        "website_supermarket_list.StoreAutocompleteComponent",
        StoreAutocompleteComponent
    );
