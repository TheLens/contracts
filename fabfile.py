# -*- coding: utf-8 -*-

'''
Methods for commiting app to Github.
It should never deploy to the server or S3.
That should be left to Travis CI and the server calling git pull.
'''

from fabric.api import local
from contracts import PROJECT_DIR

APP_DIR = '%s/contracts' % PROJECT_DIR
CONFS_DIR = '%s/confs' % PROJECT_DIR
CSS_DIR = '%s/contracts/static/css' % PROJECT_DIR
DATA_DIR = '%s/data' % PROJECT_DIR
DATAMANAGEMENT_DIR = '%s/contracts/datamanagement' % PROJECT_DIR
DOCS_DIR = '%s/docs' % PROJECT_DIR
# FONTS_DIR = '%s/contracts/static/fonts' % PROJECT_DIR
IMAGES_DIR = '%s/contracts/static/css/images' % PROJECT_DIR
JS_DIR = '%s/contracts/static/js' % PROJECT_DIR
LIB_DIR = '%s/contracts/lib' % PROJECT_DIR
PICTURES_DIR = '%s' % PROJECT_DIR + '/contracts/static/pictures'
SCRIPTS_DIR = '%s/scripts' % PROJECT_DIR
TEMPLATE_DIR = '%s/contracts/templates' % PROJECT_DIR
TESTS_DIR = '%s/tests' % PROJECT_DIR


def repo():
    '''/'''

    local('git add %s/.coveragerc' % PROJECT_DIR)
    local('git add %s/.gitignore' % PROJECT_DIR)
    # local('git add %s/.pylintrc' % PROJECT_DIR)
    local('git add %s/.travis.yml' % PROJECT_DIR)
    # local('git add %s/MANIFEST.in' % PROJECT_DIR)
    local('git add %s/README.md' % PROJECT_DIR)
    local('git add %s/fabfile.py' % PROJECT_DIR)
    local('git add %s/requirements.txt' % PROJECT_DIR)
    # local('git add %s/setup.py' % PROJECT_DIR)


def confs():
    '''/confs'''

    local('git add %s/app.ini' % CONFS_DIR)
    local('git add %s/contracts.conf' % CONFS_DIR)


def data():
    '''/data'''

    local('git add %s/dist.all.last.txt' % DATA_DIR)
    local('git add %s/dist.female.first.txt' % DATA_DIR)
    local('git add %s/dist.male.first.txt' % DATA_DIR)
    local('git add %s/skiplist.txt' % DATA_DIR)


def docs():
    '''/docs/'''

    local('git add %s/' % DOCS_DIR)

    # local('git add %s/build.rst' % DOCS_DIR)
    # local('git add %s/conf.py' % DOCS_DIR)
    # local('git add %s/database.rst' % DOCS_DIR)
    # local('git add %s/index.rst' % DOCS_DIR)
    # local('git add %s/Makefile' % DOCS_DIR)
    # local('git add %s/misc.rst' % DOCS_DIR)
    # local('git add %s/scrape.rst' % DOCS_DIR)
    # local('git add %s/tests.rst' % DOCS_DIR)


def contracts():
    '''/contracts/'''

    local('git add %s/__init__.py' % APP_DIR)
    local('git add %s/app.py' % APP_DIR)
    local('git add %s/models.py' % APP_DIR)
    local('git add %s/views.py' % APP_DIR)


def datamanagement():
    '''/contracts/datamanagement'''

    local('git add %s/__init__.py' % DATAMANAGEMENT_DIR)
    local('git add %s/backup.py' % DATAMANAGEMENT_DIR)
    local('git add %s/daily_linker.py' % DATAMANAGEMENT_DIR)
    local('git add %s/emailer.py' % DATAMANAGEMENT_DIR)
    local('git add %s/lens_doc_cloud_sync.py' % DATAMANAGEMENT_DIR)
    local('git add %s/main.py' % DATAMANAGEMENT_DIR)
    local('git add %s/vendor_scraper.py' % DATAMANAGEMENT_DIR)


def datamanagement_lib():
    '''/contracts/datamanagement/lib'''

    local('git add %s/lib/__init__.py' % DATAMANAGEMENT_DIR)
    local('git add %s/lib/models.py' % DATAMANAGEMENT_DIR)
    local('git add %s/lib/utilities.py' % DATAMANAGEMENT_DIR)


def lib():
    '''/contracts/lib'''

    local('git add %s/__init__.py' % LIB_DIR)
    local('git add %s/models.py' % LIB_DIR)
    local('git add %s/vaultclasses.py' % LIB_DIR)


def css():
    '''/contracts/static/css'''

    local('git add %s/banner.css' % CSS_DIR)
    local('git add %s/chosen.css' % CSS_DIR)
    local('git add %s/contracts.css' % CSS_DIR)
    local('git add %s/foundation.css' % CSS_DIR)
    local('git add %s/icons.css' % CSS_DIR)
    local('git add %s/lens.css' % CSS_DIR)
    local('git add %s/reset.css' % CSS_DIR)
    local('git add %s/style.css' % CSS_DIR)
    local('git add %s/stylesheet.css' % CSS_DIR)
    local('git add %s/ui.css' % CSS_DIR)
    local('git add %s/workplace.css' % CSS_DIR)
    local('git add %s/workspace.css' % CSS_DIR)


def images():
    '''/contracts/static/css/images'''

    local('git add %s/chosen-sprite.png' % IMAGES_DIR)


def js():
    '''/contracts/static/js'''

    local('git add %s/chosen.jquery.min.js' % JS_DIR)
    local('git add %s/contracts.js' % JS_DIR)
    local('git add %s/foundation.min.js' % JS_DIR)
    local('git add %s/jquery-1.11.0.min.js' % JS_DIR)
    local('git add %s/jquery.tablesorter.min.js' % JS_DIR)
    local('git add %s/lens.js' % JS_DIR)


def js_models():
    '''/contracts/static/js/models'''

    local('git add %s/models/search_facets.js' % JS_DIR)
    local('git add %s/models/search_query.js' % JS_DIR)


def js_templates():
    '''/contracts/static/js/templates'''

    local('git add %s/templates/search_box.jst' % JS_DIR)
    local('git add %s/templates/search_facet.jst' % JS_DIR)
    local('git add %s/templates/search_input.jst' % JS_DIR)
    local('git add %s/templates/templates.js' % JS_DIR)


def js_utils():
    '''/contracts/static/js/utils'''

    local('git add %s/utils/backbone_extensions.js' % JS_DIR)
    local('git add %s/utils/hotkeys.js' % JS_DIR)
    local('git add %s/utils/inflector.js' % JS_DIR)
    local('git add %s/utils/jquery_extensions.js' % JS_DIR)
    local('git add %s/utils/search_parser.js' % JS_DIR)


def js_views():
    '''/contracts/static/js/views'''

    local('git add %s/views/search_box.js' % JS_DIR)
    local('git add %s/views/search_facet.js' % JS_DIR)
    local('git add %s/views/search_input.js' % JS_DIR)


def templates():
    '''/contracts/templates'''

    local('git add %s/banner.html' % TEMPLATE_DIR)
    local('git add %s/contract.html' % TEMPLATE_DIR)
    local('git add %s/documentcloud.html' % TEMPLATE_DIR)
    local('git add %s/email.html' % TEMPLATE_DIR)
    local('git add %s/footer.html' % TEMPLATE_DIR)
    local('git add %s/head.html' % TEMPLATE_DIR)
    local('git add %s/index.html' % TEMPLATE_DIR)
    local('git add %s/js.html' % TEMPLATE_DIR)
    local('git add %s/search-area.html' % TEMPLATE_DIR)
    local('git add %s/select.html' % TEMPLATE_DIR)
    local('git add %s/table.html' % TEMPLATE_DIR)
    local('git add %s/vendors.html' % TEMPLATE_DIR)


def scripts():
    '''/scripts/'''

    local('git add %s/main.sh' % SCRIPTS_DIR)
    local('git add %s/updatebackup.sh' % SCRIPTS_DIR)


def tests():
    '''/tests/'''

    local('git add %s/__init__.py' % TESTS_DIR)
    local('git add %s/test_misc.py' % TESTS_DIR)
    local('git add %s/test_models.py' % TESTS_DIR)
    local('git add %s/test_parser.py' % TESTS_DIR)
    local('git add %s/test_pep8.py' % TESTS_DIR)
    local('git add %s/test_pylint.py' % TESTS_DIR)


# Others
def addthemall():
    '''Run through entire deployment.'''

    repo()
    confs()
    data()
    docs()
    contracts()
    datamanagement()
    datamanagement_lib()
    lib()
    css()
    images()
    js()
    js_models()
    js_templates()
    js_utils()
    js_views()
    templates()
    scripts()
    tests()


def commit(message):
    local('git commit -m "%s"' % message)


def push():
    local('git push origin master')


def pull():
    local('git pull origin master')


def github(message):
    '''Add, commit and push to Github.'''

    print message
    print type(message)

    addthemall()
    commit(message)
    push()


if __name__ == '__main__':
    pass
