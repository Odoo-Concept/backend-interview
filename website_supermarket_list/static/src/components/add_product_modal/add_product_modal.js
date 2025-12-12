/** @odoo-module **/

import {Component, onMounted, useRef, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {ProductSearch} from "@website_supermarket_list/components/product_search/product_search";

export class AddProductModal extends Component {
    static template = "website_supermarket_list.AddProductModal";
    static components = {ProductSearch};
    static props = {
        listId: Number,
        uoms: {type: Array, optional: true},
    };

    setup() {
        this.csrfToken = odoo.csrf_token;

        this.state = useState({
            isOpen: false,
            formData: {
                quantity: "1.0",
                uomId: "",
                notes: "",
            },
        });

        this.modalRef = useRef("modal");
        this.formRef = useRef("form");

        onMounted(() => {
            // Listen for modal events
            if (this.modalRef.el) {
                this.modalRef.el.addEventListener("hidden.bs.modal", () => {
                    this.onModalHidden();
                });
                this.modalRef.el.addEventListener("shown.bs.modal", () => {
                    this.onModalShown();
                });
            }
        });
    }

    onModalShown() {
        this.state.isOpen = true;
        // Reset form when modal is shown
        if (this.formRef.el) {
            this.formRef.el.reset();
            // Reset product search
            const productSearch = this.formRef.el.querySelector("#product_search");
            const productId = this.formRef.el.querySelector("#product_id");
            if (productSearch) productSearch.value = "";
            if (productId) productId.value = "";
        }
    }

    onModalHidden() {
        this.state.isOpen = false;
        this.state.formData = {
            quantity: "1.0",
            uomId: "",
            notes: "",
        };
        if (this.formRef.el) {
            this.formRef.el.reset();
        }
    }

    onSubmit(ev) {
        const form = ev.target;
        const productId = form.querySelector("#product_id");
        if (!productId || !productId.value) {
            ev.preventDefault();
            alert("Please select or create a product first.");
            return false;
        }
    }
}

registry
    .category("public_components")
    .add("website_supermarket_list.AddProductModal", AddProductModal);
