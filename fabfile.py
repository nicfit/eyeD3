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
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
################################################################################
import os
from fabric.api import run, put
from pavement import SRC_DIST_TGZ, DOC_DIST, MD5_DIST, SRC_DIST_ZIP

RELEASE_D = "~/www/eyeD3/releases"

def host_type():
    run('uname -a')

def deploy_sdist():
    put("./dist/%s" % SRC_DIST_TGZ, RELEASE_D)
    put("./dist/%s" % SRC_DIST_ZIP, RELEASE_D)
    put("./dist/%s.md5" % os.path.splitext(SRC_DIST_TGZ)[0], RELEASE_D)

def deploy_docs():
    put("./dist/%s" % DOC_DIST, RELEASE_D)
    run("tar xzf %s -C ./www/eyeD3 --strip-components=1" %
            os.path.join(RELEASE_D, DOC_DIST))

def deploy():
    deploy_sdist()
    deploy_docs()

