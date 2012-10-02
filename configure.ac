dnl
dnl  Copyright (C) 2002-2011  Travis Shirk <travis@pobox.com>
dnl
dnl  This program is free software; you can redistribute it and/or modify
dnl  it under the terms of the GNU General Public License as published by
dnl  the Free Software Foundation; either version 2 of the License, or
dnl  (at your option) any later version.
dnl
dnl  This program is distributed in the hope that it will be useful,
dnl  but WITHOUT ANY WARRANTY; without even the implied warranty of
dnl  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
dnl  GNU General Public License for more details.
dnl
dnl  You should have received a copy of the GNU General Public License
dnl  along with this program; if not, write to the Free Software
dnl  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
dnl

#pkg_version=`cat version | cut -d- -f1`
#echo "VERSION: ${pkg_version}"
AC_INIT([eyeD3], m4_esyscmd_s([cat version | cut -d- -f1]),
        [Travis Shirk <travis@pobox.com>], [eyeD3],
        [http://eyeD3.nicfit.net/])
dnl alpha beta final
PACKAGE_RELEASE_LEVEL=m4_esyscmd_s([cat version | cut -d- -f2])
AC_SUBST([PACKAGE_RELEASE_LEVEL])

EBUILD_RELEASE= 
EBUILD_VERSION=${PACKAGE_VERSION}
if test -n "$EBUILD_RELEASE"; then
    EBUILD_VERSION=${EBUILD_VERSION}-${EBUILD_RELEASE}
fi
AC_SUBST([EBUILD_VERSION])

AC_PREREQ([2.68])
AC_COPYRIGHT([GNU GPL])

BUILD_DATE=`date`
AC_SUBST([BUILD_DATE])
MANPAGE_DATE=`date +'%b. %d, %Y'`
AC_SUBST([MANPAGE_DATE])

AC_PROG_MAKE_SET

ACX_CHECK_PYTHON([2.7])

AS_AC_EXPAND(DATADIR, $datadir)
AS_AC_EXPAND(DATADIR, $DATADIR)  # Called a second time to expand ${prefix}
AC_SUBST([DATADIR])

# FIXME
#AC_CONFIG_FILES([
#                 po/Makefile \
#                 doc/eyeD3.1])
AC_CONFIG_FILES([Makefile])
AC_CONFIG_FILES([src/eyed3/info.py])
AC_OUTPUT

# FIXME
#if test -f README.t2t.in; then
#    AC_CONFIG_FILES([README.t2t])
#    export PYTHONPATH="`pwd`/src"
#    EYED3_HELP="`./bin/eyeD3 --help`"
#    AC_SUBST([EYED3_HELP])
#    AC_OUTPUT
#fi

