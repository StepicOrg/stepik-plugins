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
The application layout is as follows:

`/home/{{ stepic_user }}/instances/{{ stepic_plugins_branch }}/stepic-plugins` is the application root directory that contains the following directories:

* `/app` — source code directory
* `/app/venv` — virtualenv directory
* `/logs` — logs are stored here
* `/sandbox` — contains compilers and interpreters used by `codejail` (python, java, bash, etc.)
* `/arena` — arena is a working directory for unsafe code executed by `codejail`

The general deployment command looks like:
```
ansible-playbook -vv [-u <sudo_user> --ask-sudo-pass] -i <staging|production> <develop.yml|master.yml> [-t tags]
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

Secrets
=======
Production and staging inventory files and files with secrets (such as passwords or user names) are encrypted using [git-crypt](https://github.com/AGWA/git-crypt).

On Mac OS X install `git-crypt` using `brew`:
```
brew install git-crypt
```
After cloning a repository change directory to the repo's root and unlock encrypted files with a symmetric key:
```
git-crypt unlock /path/to/key
```
