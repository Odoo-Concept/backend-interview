/** @odoo-module **/

import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";

export class AddProductButton extends Component {
    static template = "website_supermarket_list.AddProductButton";
    static props = {
        listState: String,
    };

    get isVisible() {
        return this.props.listState !== "done";
    }
}

registry
    .category("public_components")
    .add("website_supermarket_list.AddProductButton", AddProductButton);
