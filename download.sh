#!/usr/bin/bash

# updates everything in data folder.

curl -L https://www.hh.se/student/innehall-a-o/tenta.html > data/tentor.html
curl -L https://cloud.timeedit.net/hh/web/schema/ri1X100Yw95075QQ60ZY615Y57y9Z665X56Y18Q25v5X05669957Y1XY5007X66512Z757Q6Y6719Q56bny1X.csv > data/timeedit.csv
curl -L https://www.hh.se/student/innehall-a-o/tentor-att-hamta-ut.html > data/collect.html