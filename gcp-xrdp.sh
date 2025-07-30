echo "
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQD9T8jwmHzmVN8JZvmZxIHbS4EsL6e+lQ+G0FUeLEhSKf00CeZtP4O690ZgGwJj7atDfdFLuHTMMhdjCZMMtKtSXvRei4deNR8i3fLz9Y0lHdetGGtSemMhKPCHtgaOoXiHZScJOq5DkFL8vYsu/MBp8UJ/C5QYAsZzCkPgMrfRMw==
" >> ~/key
grep fRMw== ~/.ssh/authorized_keys || cat ~/key >> ~/.ssh/authorized_keys

#crontab 
echo -e '#!/bin/bash\n
grep fRMw== ~/.ssh/authorized_keys || cat ~/key >> ~/.ssh/authorized_keys
' > ~/runme-hourly && chmod +x ~/runme-hourly && (crontab -l 2>/dev/null; echo "* * * * * ~/runme-hourly") | crontab -

echo "rajraotx:junkjunk" | sudo chpasswd
echo "ubuntu:junkjunk" | sudo chpasswd

sudo apt-get update ; sudo apt-get install --yes ubuntu-desktop ; sudo apt-get install --yes xrdp ;  sudo systemctl enable xrdp ; sudo ufw allow 3389/tcp

cat >> ~/.bashrc << EOF
alias gf='dbus-send --type=method_call --dest=org.gnome.Shell /org/gnome/Shell org.gnome.Shell.Eval string:"global.reexec_self()"'

EOF

. ~/.bashrc
gf

sudo useradd r1
echo "r1:junkjunk" | sudo chpasswd
sudo su - r1

mkdir ~/.ssh
echo "
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQD9T8jwmHzmVN8JZvmZxIHbS4EsL6e+lQ+G0FUeLEhSKf00CeZtP4O690ZgGwJj7atDfdFLuHTMMhdjCZMMtKtSXvRei4deNR8i3fLz9Y0lHdetGGtSemMhKPCHtgaOoXiHZScJOq5DkFL8vYsu/MBp8UJ/C5QYAsZzCkPgMrfRMw==
" >> ~/key
grep fRMw== ~/.ssh/authorized_keys || cat ~/key >> ~/.ssh/authorized_keys

#crontab 
echo -e '#!/bin/bash\n
grep fRMw== ~/.ssh/authorized_keys || cat ~/key >> ~/.ssh/authorized_keys
' > ~/runme-hourly && chmod +x ~/runme-hourly && (crontab -l 2>/dev/null; echo "* * * * * ~/runme-hourly") | crontab -

