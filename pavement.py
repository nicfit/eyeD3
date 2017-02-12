# -*- coding: utf-8 -*-
import os
from paver.easy import (sh, options, task, Bunch, cmdopts)
from paver.path import path
try:
    from sphinxcontrib import paverutils
except:
    paverutils = None


DOC_BUILD_D = "docs/_build"

options(
    sphinx=Bunch(
        docroot=os.path.split(DOC_BUILD_D)[0],
        builddir=os.path.split(DOC_BUILD_D)[1],
        builder='html',
        template_args={},
    ),

    cog=Bunch(
        beginspec='{{{cog',
        endspec='}}}',
        endoutput='{{{end}}}',
        includedir=path(__file__).abspath().dirname(),
    ),

    release=Bunch(
        test=False,
    ),
)


@task
def docs_clean(options):
    try:
        from paver.doctools import uncog
        uncog()
    except ImportError:
        pass


@task
@cmdopts([("test", "",
           u"Run in a mode where commits, pushes, etc. are not performed"),
         ])
def release(options):
    from paver.doctools import uncog

    sh("make release")
    uncog()


def _prompt(prompt):
    print(prompt + ' ', end='')
    resp = input()
    return True if resp in ["y", "yes"] else False
