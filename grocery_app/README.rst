==========================================
Grocery App - Your Shopping List Manager
==========================================

Welcome! 👋
===========

Ever forget what you needed at the grocery store? Or wish you could share your shopping list with family members? The Grocery App is here to help!

This Odoo module makes managing your grocery shopping lists simple and organized. Create lists, add items, track what you've bought, and never forget an item again.

What Can You Do?
================

✨ **Create Multiple Lists**
   Organize your shopping by creating separate lists for different purposes - weekly groceries, party shopping, or that special recipe you've been wanting to try.

👤 **Assign Responsibility**
   Each list has a responsible person who manages it. Perfect for families or teams where different people handle different shopping trips.

📝 **Add Products with Quantities**
   Not just "milk" but "2 gallons of milk". Add products from your Odoo product catalog with the exact quantities you need.

✅ **Track Your Progress**
   Check off items as you shop. See at a glance what you've bought and what's still on your list.

🔄 **Smart Status Updates**
   The list automatically knows when you're done shopping - no manual work needed!

How It Works
============

The app uses three simple states to track your shopping journey:

1. **Draft** 📋
   This is where you start. Add all the items you need, adjust quantities, and organize your list. You can edit everything freely at this stage.

2. **In Progress** 🛒
   Ready to hit the store? Click "Start Shopping" and your list moves to "In Progress". Now you can check off items as you put them in your cart. Perfect for using on your phone while shopping!

3. **Completed** ✅
   Once you've checked off all items, the list automatically marks itself as completed. Or you can manually complete it if you're sure everything is done.

Who Can Do What?
================

🔒 **Security Made Simple**

* **Everyone** can see all grocery lists - great for transparency in families or teams
* **Only you** can edit your own lists - no one can mess with your shopping plans
* **Only the responsible person** can mark items as purchased - prevents accidental check-offs

This means if you create a list and assign it to yourself, only you can check off items. Other users can see the list and add items, but they can't mark things as purchased. This keeps your shopping accurate!

What You'll See
===============

📊 **List View**
   See all your lists at a glance with:
   - List name
   - Who's responsible
   - Current status (color-coded!)
   - How many items total
   - How many you've purchased
   - Completion percentage (with a nice progress bar)

📝 **Form View**
   When you open a list, you'll see:
   - A status bar showing where you are in the workflow
   - Action buttons ("Start Shopping", "Complete List", etc.)
   - Statistics showing your progress
   - An editable list of items where you can:
     * Add products
     * Set quantities
     * Check off purchased items
     * Reorder items by dragging

🎯 **Search & Filter**
   Find lists quickly by:
   - Status (Draft, In Progress, Completed)
   - Responsible user
   - List name
   - Or create custom filters

Smart Features
==============

🧠 **Automatic Completion**
   When you check off the last item, the list automatically moves to "Completed". No need to click anything!

🔄 **Smart Reopening**
   If you uncheck an item from a completed list, it automatically goes back to "In Progress" - because you're clearly not done yet!

🚫 **Validation**
   The app won't let you complete a list if:
   - There are no items (what's the point?)
   - Some items aren't checked off (you'd forget something!)

Getting Started
===============

Installation
------------

1. Make sure you have Odoo 18.0 installed
2. Copy the ``grocery_app`` folder to your Odoo addons directory
3. Restart your Odoo server
4. Go to Apps menu and update the apps list
5. Search for "Grocery App" or "Grocery List Management"
6. Click the Install button

That's it! You're ready to start shopping smarter.

Creating Your First List
-------------------------

1. Go to **Grocery Lists** in the main menu
2. Click **Create** (or the big "+" button)
3. Give your list a name - something memorable like "Weekly Groceries" or "Birthday Party Shopping"
4. You'll automatically be set as the responsible user (you can change this if needed)
5. Click on the **Items** tab
6. Click **Add a line** to start adding products
7. Select a product, set the quantity you need, and you're done!

The list starts in "Draft" status, so you can add and remove items freely.

Going Shopping
--------------

When you're ready to hit the store:

1. Open your grocery list
2. Click the **"Start Shopping"** button (it's highlighted in green)
3. Your list status changes to "In Progress"
4. As you shop, check off items by clicking the toggle next to each item
5. Watch your completion percentage grow!
6. When you check off the last item, the list automatically completes itself

💡 **Tip:** Keep the list open on your phone while shopping. The real-time updates make it easy to track your progress!

Managing Items
---------------

**Adding Items**
   Click "Add a line" in the Items tab, select a product, and set the quantity.

**Changing Quantities**
   Just click on the quantity field and type a new number. The app ensures quantities are always greater than zero.

**Reordering Items**
   Use the handle (⋮⋮) on the left to drag items up or down. Organize your list by aisle, priority, or however makes sense to you!

**Marking as Purchased**
   Only the responsible user can check off items. This prevents accidental check-offs and keeps your list accurate.

**Removing Items**
   Click the trash icon to remove an item. The list statistics update automatically.

For Developers
===============

If you're a developer working with this module, here's what you need to know:

Technical Overview
------------------

**Models**

* ``grocery.list`` - The main shopping list model
  * Fields: name, responsible_user_id, status, item_ids
  * Computed fields: item_count, purchased_count, pending_count, completion_percentage
  * Methods: action_start_progress(), action_complete(), _auto_update_status()

* ``grocery.list.item`` - Individual items in a list
  * Fields: list_id, product_id, quantity, purchased, sequence
  * Methods: _check_purchase_permission(), _update_list_status()

**Dependencies**

* ``base`` - Core Odoo functionality
* ``product`` - Product catalog integration

**Security**

* Access rights: All users can read, users can only modify their own lists
* Record rules: Enforced at database level
* Permission checks: Python-level validation for purchase status changes

**Code Structure**

::

    grocery_app/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init__.py
    │   ├── grocery_list.py          # Main list model
    │   └── grocery_list_item.py     # Item model
    ├── views/
    │   ├── grocery_list_views.xml   # List views and forms
    │   ├── grocery_list_item_views.xml
    │   └── menu_views.xml           # Menu structure
    ├── security/
    │   ├── ir.model.access.csv     # Access rights
    │   └── grocery_list_security.xml # Record rules
    ├── static/
    │   └── description/
    │       └── icon.svg
    └── README.rst

Best Practices Used
-------------------

✅ Standard Odoo ORM patterns  
✅ Proper use of ``@api.depends`` for computed fields  
✅ Validation using ``@api.constrains``  
✅ Record rules for security enforcement  
✅ Clean, modular code structure  
✅ Permission checks at multiple levels (Python + view)  

Version
=======

Current Version: **18.0.1.0.0**

Compatible with: Odoo 18.0

---

Need Help?
==========

If you have questions or run into issues:

1. Check that all dependencies are installed
2. Make sure you're using Odoo 18.0
3. Verify the module is properly installed and activated
4. Check the Odoo logs for any error messages

Happy Shopping! 🛒✨
