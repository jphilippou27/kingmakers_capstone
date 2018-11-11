#! /bin/bash

python3 load_expends.py expends18
echo "expenditures table loaded"

python3 load_cands.py cands18
echo "candidates table loaded"

python3 load_indivs.py indivs18
echo "individual contributions table loaded"

python3 load_pacs2pacs.py pac_other18
echo "pac-to-pac contributions table loaded"

python3 load_pacs2cands.py pacs18
echo "pac-to-candidate contributions table loaded"

python3 load_cmtes.py cmtest18
echo "pac-to-candidate contributions table loaded"
