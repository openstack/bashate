#!/bin/bash

FOO=<<EOF

 this is a file
  that does not obey our indenting
 or our line length -------------------------------------------------

EOF

cat <<EOF > /tmp/tofile

 this is a file
  that does not obey our indenting
 or our line length -------------------------------------------------

EOF

cat << 'EOF' | sed 's/foo/bar'

 this is a file
  that does not obey our indenting
 or our line length -------------------------------------------------

EOF

cat <<"EOF"

 this is a file
  that does not obey our indenting
 or our line length -------------------------------------------------

EOF

cat > foo <<BLAH

 this is a file
  that does not obey our indenting
 or our line length -------------------------------------------------


BLAH
