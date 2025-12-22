# -*- coding: utf-8 -*-
from odoo import _, http
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class SupermarketListPortal(CustomerPortal):
    def _get_error_message(self, code):
        return {
            "missing_name": _("Please provide a list name."),
            "create_denied": _("You do not have access to create supermarket lists."),
            "create_failed": _("Unable to create the list."),
            "item_missing_name": _("Please provide a product name."),
            "item_invalid_qty": _("Quantity must be a positive number."),
            "item_create_failed": _("Unable to add the item to the list."),
            "list_done": _("Cannot add items to a completed list."),
            "line_update_failed": _("Unable to update this item."),
            "list_incomplete": _("All items must be purchased before completing the list."),
            "action_denied": _("You do not have access to update this list."),
            "action_failed": _("Unable to update the list."),
        }.get(code)

    def _supermarket_list_domain(self):
        return [("responsible_id", "=", request.env.user.id)]

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "supermarket_list_count" in counters:
            List = request.env["supermarket.list"]
            values["supermarket_list_count"] = (
                List.search_count(self._supermarket_list_domain())
                if List.has_access("read")
                else 0
            )
        return values

    @http.route(
        [
            "/my/supermarket-lists",
            "/my/supermarket-lists/page/<int:page>",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_supermarket_lists(self, page=1, **kwargs):
        values = self._prepare_portal_layout_values()
        list_model = request.env["supermarket.list"]
        domain = self._supermarket_list_domain()

        pager = portal_pager(
            url="/my/supermarket-lists",
            total=list_model.search_count(domain),
            page=page,
            step=self._items_per_page,
        )
        lists = list_model.search(
            domain, order="id desc", limit=self._items_per_page, offset=pager["offset"]
        )

        values.update(
            {
                "lists": lists,
                "page_name": "supermarket_list",
                "pager": pager,
                "default_url": "/my/supermarket-lists",
                "error_message": self._get_error_message(kwargs.get("error")),
            }
        )
        request.session["my_supermarket_list_history"] = lists.ids[:100]
        return request.render("supermarket_list.portal_my_supermarket_lists", values)

    @http.route(
        ["/my/supermarket-lists/create"],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def portal_create_supermarket_list(self, **post):
        name = (post.get("name") or "").strip()
        if not name:
            return request.redirect("/my/supermarket-lists?error=missing_name")
        try:
            list_record = request.env["supermarket.list"].create(
                {"name": name, "responsible_id": request.env.user.id}
            )
        except AccessError:
            return request.redirect("/my/supermarket-lists?error=create_denied")
        except ValidationError:
            return request.redirect("/my/supermarket-lists?error=create_failed")
        return request.redirect(f"/my/supermarket-lists/{list_record.id}")

    @http.route(["/my/supermarket-lists/<int:list_id>"], type="http", auth="user", website=True)
    def portal_my_supermarket_list_detail(self, list_id, **kwargs):
        list_record = request.env["supermarket.list"].browse(list_id)
        if not list_record.exists():
            return request.redirect("/my")
        try:
            list_record.check_access_rights("read")
            list_record.check_access_rule("read")
        except (AccessError, MissingError):
            return request.redirect("/my")

        values = self._prepare_portal_layout_values()
        values.update(
            {
                "list_record": list_record,
                "page_name": "supermarket_list_detail",
                "error_message": self._get_error_message(kwargs.get("error")),
            }
        )
        return request.render("supermarket_list.portal_my_supermarket_list_detail", values)

    @http.route(
        ["/my/supermarket-lists/<int:list_id>/add-item"],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def portal_add_supermarket_item(self, list_id, **post):
        list_record = request.env["supermarket.list"].browse(list_id)
        if not list_record.exists():
            return request.redirect("/my/supermarket-lists")
        try:
            list_record.check_access_rights("write")
            list_record.check_access_rule("write")
        except (AccessError, MissingError):
            return request.redirect(f"/my/supermarket-lists/{list_id}?error=action_denied")

        product_name = (post.get("product_name") or "").strip()
        if not product_name:
            return request.redirect(f"/my/supermarket-lists/{list_id}?error=item_missing_name")

        quantity_raw = post.get("quantity") or "1"
        try:
            quantity = float(quantity_raw)
            if quantity <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return request.redirect(f"/my/supermarket-lists/{list_id}?error=item_invalid_qty")

        try:
            request.env["supermarket.list.line"].create(
                {
                    "list_id": list_record.id,
                    "product_name": product_name,
                    "quantity": quantity,
                }
            )
        except ValidationError:
            error_code = "list_done" if list_record.state == "done" else "item_create_failed"
            return request.redirect(f"/my/supermarket-lists/{list_id}?error={error_code}")
        except AccessError:
            return request.redirect(f"/my/supermarket-lists/{list_id}?error=item_create_failed")

        return request.redirect(f"/my/supermarket-lists/{list_id}")

    @http.route(
        ["/my/supermarket-lists/line/toggle"],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def portal_toggle_supermarket_item(self, **post):
        line_id = int(post.get("line_id") or 0)
        is_purchased = post.get("is_purchased") in ("1", "true", "True", "on")
        line = request.env["supermarket.list.line"].browse(line_id)
        if not line.exists():
            return request.redirect("/my/supermarket-lists")
        list_id = line.list_id.id
        try:
            line.check_access_rights("write")
            line.check_access_rule("write")
            line.write({"is_purchased": is_purchased})
        except (AccessError, ValidationError):
            return request.redirect(f"/my/supermarket-lists/{list_id}?error=line_update_failed")
        return request.redirect(f"/my/supermarket-lists/{list_id}")

    @http.route(
        ["/my/supermarket-lists/<int:list_id>/start"],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def portal_start_supermarket_list(self, list_id, **post):
        list_record = request.env["supermarket.list"].browse(list_id)
        if not list_record.exists():
            return request.redirect("/my/supermarket-lists")
        try:
            list_record.check_access_rights("write")
            list_record.check_access_rule("write")
            list_record.action_start()
        except AccessError:
            return request.redirect(f"/my/supermarket-lists/{list_id}?error=action_denied")
        except ValidationError:
            return request.redirect(f"/my/supermarket-lists/{list_id}?error=action_failed")
        return request.redirect(f"/my/supermarket-lists/{list_id}")

    @http.route(
        ["/my/supermarket-lists/<int:list_id>/done"],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def portal_done_supermarket_list(self, list_id, **post):
        list_record = request.env["supermarket.list"].browse(list_id)
        if not list_record.exists():
            return request.redirect("/my/supermarket-lists")
        try:
            list_record.check_access_rights("write")
            list_record.check_access_rule("write")
            list_record.action_mark_done()
        except AccessError:
            return request.redirect(f"/my/supermarket-lists/{list_id}?error=action_denied")
        except ValidationError:
            return request.redirect(f"/my/supermarket-lists/{list_id}?error=list_incomplete")
        return request.redirect(f"/my/supermarket-lists/{list_id}")
