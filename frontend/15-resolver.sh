#!/bin/sh
set -eu
# Nginx usa su propio resolver y NO aplica los dominios "search" de /etc/resolv.conf.
# En Kubernetes, un nombre corto como "vehicles" no resuelve con ese resolver: se usa
# el FQDN del Service (vehicles.<namespace>.svc.cluster.local). En Docker Compose no hay
# dominio *.svc.cluster.local y el DNS embebido de Docker resuelve el nombre corto.
RESOLV="${RESOLV_CONF:-/etc/resolv.conf}"
dns=$(awk '/^nameserver/ {print $2; exit}' "$RESOLV")
search=$(awk '/^search/ {print $2; exit}' "$RESOLV")
suffix=""
case "$search" in
  *.svc.cluster.local) suffix=".$search" ;;
esac
{
  printf 'resolver %s valid=10s ipv6=off;\n' "$dns"
  printf 'set $vehicles_host vehicles%s;\n' "$suffix"
  printf 'set $tickets_host tickets%s;\n' "$suffix"
} > /tmp/resolver.conf
