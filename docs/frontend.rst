.. _frontend:

Frontend Documentation
=======================

This section contains the documentation for the React/TypeScript frontend application.

Overview
--------

The SnapCheck frontend is a React application built with TypeScript, Vite, and Material-UI.
It provides a user interface for quality control of snap images.

Architecture
------------

The frontend follows a component-based architecture with:

- **Components**: Reusable UI components organized by function
  
  - ``elements/``: Basic UI elements (images, inputs, etc.)
  - ``files/``: File management components
  - ``lib/``: Library components (buttons, tables, etc.)
  - ``specials/``: Special-purpose components (rating inputs, etc.)

- **Contexts**: React contexts for state management
  
  - ``AppDataContext``: Application-level data
  - ``ModalContext``: Modal dialog management
  - ``SettingsContext``: User settings

- **Pages**: Top-level page components
  
  - ``main/``: Main application pages (board view, etc.)

- **API**: Auto-generated TypeScript client from OpenAPI specs

TypeDoc Documentation
---------------------

The complete API reference for all React components, hooks, contexts, and utilities
is available in the TypeDoc-generated documentation:

.. raw:: html

   <p><a href="_frontend-docs/index.html" target="_blank">
   Open Frontend TypeDoc Documentation
   </a></p>

Building the Documentation
---------------------------

To regenerate the frontend documentation:

.. code-block:: bash

   cd snapcheck-front
   npm install
   npm run docs

This will generate the TypeDoc documentation in ``docs/_static/frontend-docs/``.
