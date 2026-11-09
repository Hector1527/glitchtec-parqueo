#!/bin/sh
set -eu
dns=$(awk '/^nameserver/ {print $2; exit}' /etc/resolv.conf)
printf 'resolver %s valid=10s ipv6=off;\n' "$dns" > /tmp/resolver.conf
