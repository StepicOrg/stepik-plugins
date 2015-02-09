Install/Activate Ansible
========================
Create a new python 2.7 virtualenv and install the `ansible` package into it.
```
mkvirtualenv --python=`which python2.7` ansible
pip install ansible
```
or activate previously created virtualenv with ansible installed:
```
workon ansible
```

Deployment
==========
```
ansible-playbook -vv -i <staging|production> <develop.yml|master.yml>
```

Update the application after the source code has changed:
```
ansible-playbook -vv -i staging develop.yml -t app
```

Update configs only (supervisor and local_settings.py) and restart the application:
```
ansible-playbook -vv -i staging develop.yml -t config
```

Install/update sandboxes and apparmor profiles:
```
ansible-playbook -vv -i staging develop.yml -t sandbox
```

Run sandbox tests:
```
ansible-playbook -vv -i staging develop.yml -t test
```
