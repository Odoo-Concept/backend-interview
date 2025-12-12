/** @odoo-module **/

import {Component} from "@odoo/owl";
import {AutoCompleteWithPages} from "@website/components/autocomplete_with_pages/autocomplete_with_pages";
import {rpc} from "@web/core/network/rpc";

export class StoreAutoComplete extends Component {
    static props = {
        targetDropdown: {type: HTMLElement},
    };
    static template = "website_supermarket_list.StoreAutoComplete";
    static components = {AutoCompleteWithPages};

    setup() {
        // Initialize component lifecycle
    }

    _mapItemToSuggestion(item) {
        return {
            ...item,
            classList: "ui-autocomplete-item",
        };
    }

    get dropdownClass() {
        return "show";
    }

    get dropdownOptions() {
        return {
            position: "bottom-start",
        };
    }

    get sources() {
        return [
            {
                optionTemplate: "website_supermarket_list.StoreAutoCompleteItem",
                options: async (term) => {
                    if (!term || term.length < 2) {
                        return [];
                    }
                    try {
                        const res = await rpc("/grocery/search-stores", {
                            term: term,
                            limit: 20,
                        });
                        // Handle both direct response and JSON-RPC response format
                        const stores = res.stores || res.result?.stores || [];
                        const suggestions = stores.map((store) =>
                            this._mapItemToSuggestion({
                                label: store.name,
                                value: store.name,
                                address: store.address || "",
                            })
                        );
                        return suggestions;
                    } catch (error) {
                        console.error("Error searching stores:", error);
                        return [];
                    }
                },
            },
        ];
    }

    onSelect(selectedSuggestion, {input}) {
        const {value} = Object.getPrototypeOf(selectedSuggestion);
        if (input) {
            input.value = value;
        }
        if (this.props.targetDropdown) {
            this.props.targetDropdown.value = value;
        }
    }

    onInput({inputValue}) {
        if (this.props.targetDropdown) {
            this.props.targetDropdown.value = inputValue;
        }
    }
}
