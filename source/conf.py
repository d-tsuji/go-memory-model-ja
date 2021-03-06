# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
from recommonmark.transform import AutoStructify
from recommonmark.parser import CommonMarkParser
import os
import sys
sys.path.insert(0, os.path.abspath('ext'))

# -- Project information -----------------------------------------------------

project = 'The Go Memory Model'
copyright = '2020, d-tsuji'
author = 'd-tsuji'

# The full version, including alpha/beta/rc tags
release = ''

source_suffix = ['.rst', '.md']
source_parsers = {
    '.md': CommonMarkParser,
}

# -- General configuration ---------------------------------------------------


# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['pageinfo', 'sphinx.ext.todo', 'sphinx.ext.githubpages',
              'sphinx.ext.mathjax']  # , 'sphinxcontrib.github_ribbon']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'ja'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

[extensions]
todo_include_todos = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'traditional'
# html_theme = 'nature'
# html_theme = 'bizstyle'

pygments_style = 'sphinx'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_sidebars = {
    # add 'pageinfo.html' to display the panel.
    '**': ['localtoc.html', 'relations.html', 'sourcelink.html', 'pageinfo.html', 'searchbox.html']
}

# LaTeX の docclass 設定
latex_docclass = {'manual': 'jsbook'}

# -- Options for sphinxcontrib-githubribbon ----------------------------------
# github_ribbon_repo = 'd-tsuji/go-introduction-book'
# github_ribbon_position = 'right'
# github_ribbon_color = "gray"
