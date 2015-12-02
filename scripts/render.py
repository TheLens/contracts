# -*- coding: utf-8 -*-

'''Renders CSS for front-end.'''

from subprocess import call
from contracts import PROJECT_DIR


def render_sass():
    '''Render SCSS files.'''

    call([
        'sass',
        '%s/contracts/static/css/scss/contracts.scss' % PROJECT_DIR,
        '%s/contracts/static/css/contracts.css' % PROJECT_DIR
    ])

if __name__ == '__main__':
    render_sass()
