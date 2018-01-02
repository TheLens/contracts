"""Sphinx configuration."""

import os
import sys

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))

from contracts.constants import __VERSION__


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon']

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = 'contracts'
copyright = '2017, The Lens'
author = 'The Lens'

# |version| and |release|
version = __VERSION__
release = __VERSION__

exclude_patterns = ['_build']
pygments_style = 'sphinx'
html_theme = 'sphinx_rtd_theme'

html_static_path = ['static']
htmlhelp_basename = 'electionsdoc'
