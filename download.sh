#!/usr/bin/bash

# updates everything in data folder.

mkdir -p data

curl -L https://www.hh.se/student/innehall-a-o/tenta.html > data/tentor.html
#curl -L https://cloud.timeedit.net/hh/web/schema/ri1X100Yw95075QQ60ZY615Y57y9Z665X56Y18Q25v5X05669957Y1XY5007X66512Z757Q6Y6719Q56bny1X.csv > data/timeedit.csv
curl -L https://cloud.timeedit.net/hh/web/schema/ri1006YX5Z0067QQ6YZQ916051y5Y5665g6005X27655Yw951578X05X7yY5596X01Y7667nX6905b69QZ15Q2511Y67.csv > data/timeedit.csv
curl -L https://www.hh.se/student/innehall-a-o/tentor-att-hamta-ut.html > data/collect.html
