# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
import os
project = 'Customers Service'
copyright = '2024, Saja'
author = 'Saja'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


# Add the 'customers' directory to sys.path so Sphinx can find the modules

# Add the path to the parent directory of 'customers'
# Ensure the current directory is included
sys.path.insert(0, os.path.abspath('.'))
# Include the 'customers' directory
# Add the root directory (one level above 'customers') to sys.path
sys.path.insert(0, os.path.abspath('../'))
sys.path.insert(0, os.path.abspath('./customers'))
sys.path.insert(0, os.path.abspath('./customers/app'))
# Enable Sphinx extensions
extensions = [
    'sphinx.ext.autodoc',  # Automatically document from docstrings
    'sphinx.ext.napoleon',  # Support for Google-style and NumPy-style docstrings
    'sphinx.ext.viewcode'  # Add links to the source code
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

# Napoleon settings (for Google-style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
