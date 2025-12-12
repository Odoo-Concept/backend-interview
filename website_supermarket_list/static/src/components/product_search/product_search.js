/** @odoo-module **/

import {Component, useExternalListener, useRef, useState} from "@odoo/owl";
import {debounce} from "@web/core/utils/timing";
import {rpc} from "@web/core/network/rpc";
import {registry} from "@web/core/registry";

export class ProductSearch extends Component {
    static template = "website_supermarket_list.ProductSearch";
    static props = {
        listId: Number,
        uoms: {type: Array, optional: true},
    };

    setup() {
        this.state = useState({
            isLoading: false,
            products: [],
            searchTerm: "",
            selectedProduct: null,
            showDropdown: false,
        });

        this.searchInputRef = useRef("searchInput");
        this.productIdInputRef = useRef("productIdInput");
        this.resultsRef = useRef("results");

        this.debouncedSearch = debounce(this.searchProducts.bind(this), 300);

        // Handle clicks outside
        useExternalListener(document, "click", this._onDocumentClick);
    }

    onInput(ev) {
        const term = ev.target.value.trim();
        this.state.searchTerm = term;

        if (term.length < 2) {
            this.state.showDropdown = false;
            return;
        }

        this.debouncedSearch(term);
    }

    onFocus() {
        if (this.state.searchTerm.length >= 2 && this.state.products.length > 0) {
            this.state.showDropdown = true;
        }
    }

    onProductClick(ev) {
        ev.preventDefault();
        const productId = ev.currentTarget.dataset.productId;
        const productName = ev.currentTarget.dataset.productName;
        this.selectProduct({
            id: productId,
            name: productName,
        });
    }

    onCreateProductClick(ev) {
        ev.preventDefault();
        const term = ev.currentTarget.dataset.term;
        this.createProduct(term);
    }

    _onDocumentClick(ev) {
        if (
            this.searchInputRef.el &&
            this.resultsRef.el &&
            !this.searchInputRef.el.contains(ev.target) &&
            !this.resultsRef.el.contains(ev.target)
        ) {
            this.state.showDropdown = false;
        }
    }

    selectProduct(product) {
        this.state.selectedProduct = product;
        this.state.showDropdown = false;

        if (this.productIdInputRef.el) {
            this.productIdInputRef.el.value = product.id;
        }
        if (this.searchInputRef.el) {
            this.searchInputRef.el.value = product.name;
        }
    }

    async searchProducts(term) {
        this.state.isLoading = true;
        this.state.showDropdown = true;

        try {
            const data = await rpc("/grocery/search-products", {
                term: term,
                limit: 20,
            });
            this.state.products = data.products || [];
        } catch (error) {
            console.error("Error:", error);
            this.state.products = [];
        } finally {
            this.state.isLoading = false;
        }
    }

    async createProduct(name) {
        try {
            const data = await rpc("/grocery/create-product", {
                name: name,
                category: "",
            });
            const product = data.product;
            if (product) {
                this.selectProduct({
                    id: product.id,
                    name: product.name,
                });
            }
        } catch (error) {
            alert("Error creating product");
            console.error("Error:", error);
        }
    }
}

registry
    .category("public_components")
    .add("website_supermarket_list.ProductSearch", ProductSearch);
