/** @odoo-module **/

import {App, Component} from "@odoo/owl";
import {StoreAutoComplete} from "@website_supermarket_list/components/store_autocomplete/store_autocomplete";
import {_t} from "@web/core/l10n/translation";
import {getTemplate} from "@web/core/templates";

/**
 * Initializes autocomplete for store input field
 * @param {HTMLInputElement} input - The input element to attach autocomplete to
 * @returns {Function} Cleanup function to destroy the component
 */
export function initStoreAutocomplete(input) {
    if (!input) {
        return () => {
            // Empty cleanup function
        };
    }

    try {
        const owlApp = new App(StoreAutoComplete, {
            env: Component.env,
            dev: Component.env?.debug || false,
            getTemplate,
            props: {
                targetDropdown: input,
            },
            translatableAttributes: ["data-tooltip"],
            translateFn: _t,
        });

        const container = document.createElement("div");
        container.classList.add(
            "ui-widget",
            "ui-autocomplete",
            "ui-widget-content",
            "border-0"
        );
        document.body.appendChild(container);
        owlApp.mount(container);

        return () => {
            owlApp.destroy();
            container.remove();
        };
    } catch (error) {
        console.error("Error initializing store autocomplete:", error);
        return () => {
            // Empty cleanup function
        };
    }
}
