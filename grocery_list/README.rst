Módulo Grocery List
===================

Este repositorio contiene el módulo **Grocery List** desarrollado para **Odoo 18**.  
Su objetivo es ofrecer una solución  para **crear, gestionar y controlar listas de supermercado**, con soporte para precios de productos con asignación de responsables.

---

🚀 Funcionalidades Principales
------------------------------

Gestión de Listas
~~~~~~~~~~~~~~~~~

* Crear y gestionar listas de supermercado.
* Asignar un **usuario responsable** por lista.
* Agregar productos con su cantidad deseada.
* Marcar ítems como comprados o pendientes.
* Controlar el progreso de la lista con porcentaje completado.
* Estados de lista: **Borrador**, **En Progreso** y **Completada**.

---





🧱 Estructura del Módulo
------------------------

.. code-block:: text

    grocery_list/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── grocery_list.py
    ├── views/
    │   ├── grocery_list_views.xml
    ├── security/
    │   ├── security.xml
    │   ├── ir.model.access.csv
    │   └── rules.xml
    └── static/
        └── description/
            └── icon.png

---

🧠 Detalles Técnicos
--------------------

+-----------------------+--------------------------------------------------------------------------------------------+
| Componente            | Descripción                                                                               |
+=======================+============================================================================================+
| **Modelos**           | `grocery.list`, `grocery.list.item`, `res.config.settings`, `grocery.list.complete.wizard`.|
+-----------------------+--------------------------------------------------------------------------------------------+
| **Vistas**            | Formularios, listas, kanban.             |
+-----------------------+--------------------------------------------------------------------------------------------+
| **Seguridad**         | Grupos de usuarios (Usuario y Administrador), reglas de acceso y permisos detallados.     |
+-----------------------+--------------------------------------------------------------------------------------------+

---

🧰 Requisitos
-------------

* **Odoo 18.0+**
* **Python 3.10+**
* Dependencias: `base`, `mail`, `product`

---

⚡ Instalación
--------------

1. Clona el repositorio dentro de tu carpeta ``addons``:

   .. code-block:: bash

       git clone https://github.com/rojasarmando/backend-interview

2. Reinicia el servidor de Odoo.
3. Actualiza la lista de aplicaciones.
4. Instala **Grocery List** desde el menú *Aplicaciones*.

---

🧑‍💻 Autor
----------

**Armando Rojas**  
📧 `armando.develop@gmail.com <mailto:armando.develop@gmail.com>`_  
🌐 `Odoo Concept <https://odooconcept.com>`_

---

📘 Guía Rápida de Uso
---------------------

1. Ingresa a **Grocery → My Grocery Lists**.  
2. Crea una nueva lista, asigna un nombre y un responsable.  
3. Agrega productos, cantidades y precios (si está habilitado).  
4. Marca productos como comprados.  
5. Cambia el estado a **En Progreso** o **Completada**.  
