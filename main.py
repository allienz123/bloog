# The MIT License
# 
# Copyright (c) 2008 William T. Katz
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to 
# deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.


__author__ = 'William T. Katz'

import config
import os
import sys

# Force sys.path to have our own directory first, so we can import from it.
sys.path.insert(0, config.APP_ROOT_DIR)
sys.path.insert(1, os.path.join(config.APP_ROOT_DIR, 'utils/external'))

import logging
#import wsgiref.handlers
from firepython.middleware import FirePythonWSGI
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import webapp
from google.appengine.api import users
from handlers.bloog import blog, contact, cache_stats, timings, imagestore

# Import custom django libraries
webapp.template.register_template_library('utils.django_libs.gravatar')
webapp.template.register_template_library('utils.django_libs.description')

# Configure logging for debug if in dev environment
if config.DEBUG: logging.getLogger().setLevel(logging.DEBUG)

# Log a message each time this module get loaded.
logging.info('Loading %s, app version = %s',
             __name__, os.getenv('CURRENT_VERSION_ID'))

ROUTES = [
    ('/*$', blog.RootHandler),
    ('/403.html', blog.UnauthorizedHandler),
    ('/404.html', blog.NotFoundHandler),
    ('/([12]\d\d\d)/*$', blog.YearHandler),
    ('/([12]\d\d\d)/([01]?\d)/*$', blog.MonthHandler),
    ('/([12]\d\d\d)/([01]?\d)/([-\w]+)/*$', blog.BlogEntryHandler),
    ('/admin/cache_stats/*$', cache_stats.CacheStatsHandler),
    ('/admin/timings/*$', timings.TimingHandler),
    ('/search', blog.SearchHandler),
    ('/comment/?([\w-]+)?', blog.CommentHandler),
    ('/contact/*$', contact.ContactHandler),
    ('/imgstore/?([\w]*)/?', imagestore.PicasaImageHandler \
      if config.BLOG['picasa_image_store'] else imagestore.ImageHandler),
    ('/tag/?(\w+)?', blog.TagHandler),
    (config.BLOG['master_atom_url'] + '/*$', blog.AtomHandler),
    (config.BLOG['legacy_atom_url'] + '/*$', blog.AtomHandler), # old Atom URL from legacy blog (should redirect)
    ('/articles', blog.ArticlesHandler),
    ('/sitemap.xml', blog.SitemapHandler),
    ('/(.*)', blog.ArticleHandler)]


def main():
    path = timings.start_run()
    application = webapp.WSGIApplication(ROUTES, debug=config.DEBUG)
    if users.is_current_user_admin():
        application = FirePythonWSGI(application)
    # Attempt to fix KeyError: 'CONTENT_TYPE' that is appearing in logs; see:
    # http://code.google.com/p/googleappengine/issues/detail?id=2040
    #wsgiref.handlers.CGIHandler().run(application)
    run_wsgi_app(application)
    timings.stop_run(path)

if __name__ == "__main__":
    main()
