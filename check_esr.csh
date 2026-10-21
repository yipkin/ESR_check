#!/bin/csh -f

# If run by hand, you may need to do:
#source ~/Downloads/.venv-esr/bin/activate.csh
# and then
# python download_esr_html.py ....

# ***************************************************************************************
# Warning or Notice for myself:
#
# stty -echo affects the terminal, so if the script is interrupted before stty echo runs,
# you may need to restore it with stty echo !!
# ***************************************************************************************

if ( $1 == "" ) then

echo -n "Please type the code: "
stty -echo
set thecode = $<
stty echo
echo ""

endif


cd ~/Downloads
set py = "$HOME/Downloads/.venv-esr/bin/python"

set list = "088-2025-JUN-3 089-2025-OCT-3 091-2022 092-2023 093-2023 094-2023 095-2023 097-2023 099-2023 102-2023 103-2023 104-2023 107-2023 109-2023 110-2023 111-2023 112-2023 113-2024 115-2025 116-2025 118-2026 119-2026 120-2026 121-2026"

#set list = "118-2026"

foreach pick ( $list ) 

#ls "$pick".html

echo " $pick "

#$py download_esr_html.py -l PO-"$pick" -user kinyip -pass 'password_withsymbol' -v
$py download_esr_html.py -l PO-"$pick" -user kinyip -pass $thecode -v
mv -f  esrlist.html  "$pick".html

#grep green "$pick".html | grep '<tr>' | grep '<td>'
#grep -i red "$pick".html | grep '<tr>' | grep '<td>'
grep -i red "$pick".html | grep '<font'


end
