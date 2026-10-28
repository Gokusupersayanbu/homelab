#!/usr/bin/env bash
# Alerta por presion de memoria, no solo por swap utilizada.
set -euo pipefail
URL=$(</etc/homelab-monitor/memoria-url)
URL=${URL%%\?*}
read -r TOTAL DISP SWAP_TOTAL SWAP_FREE < <(
  awk '/^MemTotal:/ {t=$2} /^MemAvailable:/ {a=$2} /^SwapTotal:/ {st=$2} /^SwapFree:/ {sf=$2} END {print t,a,st,sf}' /proc/meminfo
)
RAM_PCT=$(( DISP * 100 / TOTAL ))
SWAP_PCT=0
if (( SWAP_TOTAL > 0 )); then
  SWAP_PCT=$(( (SWAP_TOTAL - SWAP_FREE) * 100 / SWAP_TOTAL ))
fi
read -r PSI_SOME PSI_FULL < <(
  awk '{for(i=2;i<=NF;i++){split($i,v,"=");if(v[1]=="avg300"){if($1=="some") some=v[2]; if($1=="full") full=v[2]}}} END {print some,full}' /proc/pressure/memory
)
ESTADO=up
if (( RAM_PCT < 10 || (SWAP_PCT >= 90 && RAM_PCT < 20) )); then ESTADO=down; fi
if awk -v s="$PSI_SOME" -v f="$PSI_FULL" 'BEGIN {exit !(s >= 10 || f >= 2)}'; then ESTADO=down; fi
MSG="RAM disponible ${RAM_PCT}%, Swap ${SWAP_PCT}%, PSI some ${PSI_SOME}%, full ${PSI_FULL}%"
curl --fail --silent --show-error --max-time 15 --get \
  --data-urlencode "status=$ESTADO" --data-urlencode "msg=$MSG" "$URL"
echo; echo "Estado: $ESTADO"; echo "$MSG"
