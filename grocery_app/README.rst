==========================================
Grocery App - Grocery List Management
==========================================

Overview
========

This custom Odoo module enables users to create, manage, and track grocery shopping lists in a structured and user-friendly manner.

Features
========

Core Functionality
------------------

* **Create and Manage Grocery Lists**: Users can create multiple grocery lists with descriptive names
* **Responsible User Assignment**: Each list has a designated responsible user who manages the list
* **Product Management**: Add products to lists with quantities and units of measure
* **Purchase Tracking**: Mark items as purchased or unpurchased during shopping
* **Automatic Status Updates**: List status automatically updates based on item completion

Workflow States
---------------

1. **Draft**: Initial state where products can be added, removed, and edited
2. **In Progress**: Active shopping state where items can be marked as purchased
3. **Completed**: Automatically set when all items are purchased

Security & Access Control
--------------------------

* **Role-Based Permissions**: Only the responsible user can mark items as purchased/unpurchased
* **View Access**: All users can view lists and items
* **Modification Rights**: Users can only modify their own lists
* **Record Rules**: Implemented to enforce security at the database level

User Interface
--------------

* **Tree View**: Display lists with name, responsible user, status, and item statistics
* **Form View**:

  * Statusbar showing workflow progression
  * Editable list of items with inline editing
  * Visual indication of purchased items (grayed out)
  * Progress tracking with completion percentage

* **Search & Filters**: Filter by status, responsible user, and more
* **Grouping**: Group lists by various criteria

Business Logic
--------------

* Lists cannot be marked as completed unless all items are purchased
* Status automatically updates to "Completed" when all items are purchased
* Status reverts to "In Progress" if a completed item is unchecked
* Validation prevents manual completion with unpurchased items

Technical Details
=================

Models
------

**grocery.list**

* name (Char): List name
* responsible_user_id (Many2one): Responsible user
* status (Selection): Draft/In Progress/Completed
* item_ids (One2many): Related items
* Computed fields: item_count, purchased_count, pending_count, completion_percentage

**grocery.list.item**

* list_id (Many2one): Parent grocery list
* product_id (Many2one): Product to purchase
* quantity (Float): Quantity needed
* purchased (Boolean): Purchase status
* sequence (Integer): For ordering items

Dependencies
------------

* base
* product

Files Structure
---------------

::

    grocery_app/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init__.py
    │   ├── grocery_list.py
    │   └── grocery_list_item.py
    ├── views/
    │   ├── grocery_list_views.xml
    │   ├── grocery_list_item_views.xml
    │   └── menu_views.xml
    ├── security/
    │   ├── ir.model.access.csv
    │   └── grocery_list_security.xml
    ├── static/
    │   └── description/
    │       └── icon.png
    └── README.rst

Installation
============

1. Copy the ``grocery_app`` folder to your Odoo addons directory
2. Update the apps list in Odoo
3. Search for "Grocery App" or "Grocery List Management"
4. Click Install

Usage
=====

Creating a Grocery List
-----------------------

1. Navigate to Grocery Lists > Lists > Grocery Lists
2. Click "Create"
3. Enter a name for your list
4. The current user is automatically set as responsible
5. Add items by clicking "Add a line" in the Items tab

Shopping Workflow
-----------------

1. When ready to shop, click "Start Shopping" to move to "In Progress"
2. During shopping, check off items as you purchase them
3. When all items are purchased, the list automatically moves to "Completed"
4. You can also manually complete using the "Complete List" button

Managing Items
--------------

* Add products with quantities
* Drag and drop to reorder items using the handle
* Only the responsible user can mark items as purchased
* Visual feedback: purchased items appear grayed out

Development Notes
=================

Best Practices Implemented
---------------------------

* Standard Odoo ORM usage
* Proper use of @api.depends for computed fields
* Validation using @api.constrains
* Record rules for security
* Clean, modular code structure

Version
=======

18.0.1.0.0