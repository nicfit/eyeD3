# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2012  Travis Shirk <travis@pobox.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>
################################################################################
import os
from fabric.api import run, put, local, task
from pavement import SRC_DIST_TGZ, DOC_DIST, SRC_DIST_ZIP

RELEASE_D = "~/www/eyeD3/releases"


@task
def deploy_sdist(test=False):
    '''Deploy .tgz, .zip, and .md5'''
    test = bool(test)  # string from cmd line, not-empty is True
    # These repo names are defined in ~/pypirc
    local("paver sdist upload -r {}".format("pypi" if not test else "pypitest"))
    for pkg in (SRC_DIST_TGZ, SRC_DIST_ZIP):
        put("./dist/%s" % pkg, RELEASE_D)
        local("md5sum dist/%s >> dist/%s.md5" % (pkg, pkg))
        put("./dist/%s.md5" % pkg, RELEASE_D)


@task
def deploy_docs():
    '''Deploy docs tarball and install.'''
    local("paver docdist")
    local("md5sum dist/%s >> dist/%s.md5" % (DOC_DIST, DOC_DIST))
    put("./dist/%s" % DOC_DIST, RELEASE_D)
    run("tar xzf %s -C ./www/eyeD3 --strip-components=1" %
            os.path.join(RELEASE_D, DOC_DIST))


@task
def deploy():
    deploy_sdist()
    deploy_docs()
