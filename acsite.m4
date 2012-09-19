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

AC_DEFUN([ACX_CHECK_PYTHON], [
   acx_python_major=`echo $1 | cut -f1 -d.`
   PYTHON=""
   for python in python python${acx_python_major} python$1; do
       dnl Unset to avoid cache hits that did not pass the version test
       unset ac_cv_path_PYTHON
       AC_PATH_PROGS([PYTHON], [$python])
       if test -z "${PYTHON}"; then 
           continue
       fi
       AC_MSG_CHECKING([if ${PYTHON} is version >= $1])
       version=`${PYTHON} -c 'import sys; print("%d.%d.%d" % (sys.version_info[[0]], sys.version_info[[1]], sys.version_info[[2]]))'`
       AX_COMPARE_VERSION([${version}], [ge], [$1])
       if test ${ax_compare_version} = "true"; then
           AC_MSG_RESULT([yes])
           break
       else
           AC_MSG_RESULT([no])
           PYTHON=""
       fi 
   done

   if test -z ${PYTHON}; then 
      AC_MSG_ERROR([python version $1 could not be found])
   fi
])

dnl #########################################################################
AC_DEFUN([AX_COMPARE_VERSION], [
  # Used to indicate true or false condition
  ax_compare_version=false

  # Convert the two version strings to be compared into a format that
  # allows a simple string comparison.  The end result is that a version 
  # string of the form 1.12.5-r617 will be converted to the form 
  # 0001001200050617.  In other words, each number is zero padded to four 
  # digits, and non digits are removed.
  AS_VAR_PUSHDEF([A],[ax_compare_version_A])
  A=`echo "$1" | sed -e 's/\([[0-9]]*\)/Z\1Z/g' \
                     -e 's/Z\([[0-9]]\)Z/Z0\1Z/g' \
                     -e 's/Z\([[0-9]][[0-9]]\)Z/Z0\1Z/g' \
                     -e 's/Z\([[0-9]][[0-9]][[0-9]]\)Z/Z0\1Z/g' \
                     -e 's/[[^0-9]]//g'`

  AS_VAR_PUSHDEF([B],[ax_compare_version_B])
  B=`echo "$3" | sed -e 's/\([[0-9]]*\)/Z\1Z/g' \
                     -e 's/Z\([[0-9]]\)Z/Z0\1Z/g' \
                     -e 's/Z\([[0-9]][[0-9]]\)Z/Z0\1Z/g' \
                     -e 's/Z\([[0-9]][[0-9]][[0-9]]\)Z/Z0\1Z/g' \
                     -e 's/[[^0-9]]//g'`

  dnl # In the case of le, ge, lt, and gt, the strings are sorted as necessary 
  dnl # then the first line is used to determine if the condition is true. 
  dnl # The sed right after the echo is to remove any indented white space.
  m4_case(m4_tolower($2),
  [lt],[
    ax_compare_version=`echo "x$A
x$B" | sed 's/^ *//' | sort -r | sed "s/x${A}/false/;s/x${B}/true/;1q"`
  ],
  [gt],[
    ax_compare_version=`echo "x$A
x$B" | sed 's/^ *//' | sort | sed "s/x${A}/false/;s/x${B}/true/;1q"`
  ],
  [le],[
    ax_compare_version=`echo "x$A
x$B" | sed 's/^ *//' | sort | sed "s/x${A}/true/;s/x${B}/false/;1q"`
  ],
  [ge],[
    ax_compare_version=`echo "x$A
x$B" | sed 's/^ *//' | sort -r | sed "s/x${A}/true/;s/x${B}/false/;1q"`
  ],[
    dnl Split the operator from the subversion count if present.
    m4_bmatch(m4_substr($2,2),
    [0],[
      # A count of zero means use the length of the shorter version.
      # Determine the number of characters in A and B.
      ax_compare_version_len_A=`echo "$A" | awk '{print(length)}'`
      ax_compare_version_len_B=`echo "$B" | awk '{print(length)}'`
 
      # Set A to no more than B's length and B to no more than A's length.
      A=`echo "$A" | sed "s/\(.\{$ax_compare_version_len_B\}\).*/\1/"`
      B=`echo "$B" | sed "s/\(.\{$ax_compare_version_len_A\}\).*/\1/"`
    ],
    [[0-9]+],[
      # A count greater than zero means use only that many subversions 
      A=`echo "$A" | sed "s/\(\([[0-9]]\{4\}\)\{m4_substr($2,2)\}\).*/\1/"`
      B=`echo "$B" | sed "s/\(\([[0-9]]\{4\}\)\{m4_substr($2,2)\}\).*/\1/"`
    ],
    [.+],[
      AC_WARNING(
        [illegal OP numeric parameter: $2])
    ],[])

    # Pad zeros at end of numbers to make same length.
    ax_compare_version_tmp_A="$A`echo $B | sed 's/./0/g'`"
    B="$B`echo $A | sed 's/./0/g'`"
    A="$ax_compare_version_tmp_A"

    # Check for equality or inequality as necessary.
    m4_case(m4_tolower(m4_substr($2,0,2)),
    [eq],[
      test "x$A" = "x$B" && ax_compare_version=true
    ],
    [ne],[
      test "x$A" != "x$B" && ax_compare_version=true
    ],[
      AC_WARNING([illegal OP parameter: $2])
    ])
  ])

  AS_VAR_POPDEF([A])dnl
  AS_VAR_POPDEF([B])dnl

  dnl # Execute ACTION-IF-TRUE / ACTION-IF-FALSE.
  if test "$ax_compare_version" = "true" ; then
    m4_ifvaln([$4],[$4],[:])dnl
    m4_ifvaln([$5],[else $5])dnl
  fi
]) dnl AX_COMPARE_VERSION

dnl AS_AC_EXPAND(VAR, CONFIGURE_VAR)
dnl
dnl example
dnl AS_AC_EXPAND(SYSCONFDIR, $sysconfdir)
dnl will set SYSCONFDIR to /usr/local/etc if prefix=/usr/local

AC_DEFUN([AS_AC_EXPAND],
[
  EXP_VAR=[$1]
  FROM_VAR=[$2]

  dnl first expand prefix and exec_prefix if necessary
  prefix_save=$prefix
  exec_prefix_save=$exec_prefix

  dnl if no prefix given, then use /usr/local, the default prefix
  if test "x$prefix" = "xNONE"; then
    prefix=$ac_default_prefix
  fi
  dnl if no exec_prefix given, then use prefix
  if test "x$exec_prefix" = "xNONE"; then
    exec_prefix=$prefix
  fi

  full_var="$FROM_VAR"
  dnl loop until it doesn't change anymore
  while true; do
    new_full_var="`eval echo $full_var`"
    if test "x$new_full_var"="x$full_var"; then break; fi
    full_var=$new_full_var
  done

  dnl clean up
  full_var=$new_full_var
  AC_SUBST([$1], "$full_var")

  dnl restore prefix and exec_prefix
  prefix=$prefix_save
  exec_prefix=$exec_prefix_save
])
