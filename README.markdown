             8I                                                       I8
             8I                                                       I8
             8I      gg                                         gg 88888888
             8I      ""                                         ""    I8
       ,gggg,8I      gg    ,gggg,gg   ,ggg,,ggg,     ,gggg,gg   gg    I8
      dP"  "Y8I      8I   dP"  "Y8I  ,8" "8P" "8,   dP"  "Y8I   88    I8
     i8'    ,8I     ,8I  i8'    ,8I  I8   8I   8I  i8'    ,8I   88   ,I8,
    ,d8,   ,d8b,  _,d8I ,d8,   ,d8b,,dP   8I   Yb,,d8,   ,d8I _,88,_,d88b,
    P"Y8888P"`Y8888P"888P"Y8888P"`Y88P'   8I   `Y8P"Y8888P"8888P""Y88P""Y8
                   ,d8I'                                 ,d8I'
                 ,dP'8I                                ,dP'8I
                ,8"  8I                               ,8"  8I
                I8   8I    The Django Git Frontend    I8   8I
                `8, ,8I                               `8, ,8I
                 `Y8P"                                 `Y8P"

# About
djangit is a git web frontend written with django and dulwich.

# Requirements

Installable from pypi:
- Django
- Dulwich

Other requirements:
- Git

# Installing
Add this to your `INSTALLED_APPS` in settings.py:

    'django.contrib.markup',
    'djangit',
    
## On DigitalOcean
Using Ansible you can get Djangit running on a DigitalOcean instance with just one command 
(not counting cloning and setting up a virtualenv)!

1. `git clone https://github.com/valberg/djangit.git`
2. `cd djangit/`
3. Create a virtualenv
4. In virtualenv: `pip install -r requirements_dev.txt`
5. `cd ansible/`
6. `mv digital_ocean_credentials.yml.template digital_ocean_credentials.yml`
7. Add `client_id`, `api_key` and `ssh_key_ids` to `digital_ocean_credentials.yml` (more details in the file)
8. Deploy: `ansible-playbook -i localhost, digital_ocean.yml`

# License
We need a license!

# Hacking

## Requirements

- [Vagrant](http://vagrantup.com) *
- [Ansible](http://docs.ansible.com/) *
- [SASS](http://sass-lang.com/) (for compiling .scss to .css)

\* Hard requirement

## Setup

For starters, install the requirements (at least the ones marked as hard requirements) listed above.

When that is done, install the required python packages in a virtual environment:

    pip install -r requirements_dev.txt

Next, run:

    inv up

This will create a new Vagrant instance and provision it using Ansible.

**Note**: This can take some time, depending on your internet connection,
since a Ubuntu 14.04 base box needs to be downloaded and then upgraded
via Ansible.

You should now be ready to hack on Djangit!

*If anything doesn't work, please create an issue*

## Tasks

Djangit uses [Invoke](http://pyinvoke.org) to run tasks associated with development. Each task is runnable using `inv <taskname>`.

### Start
To both start the vagrant box (provision if needed) and then run Djangos `runserver` use `inv start`.

This command is comprised of two other commands `up` and `serve`. So, to only start the vagrant box run `inv up`, and to only run the development server (requires a running vagrant box) run `inv serve`.

To access the running development version of Djangit use: [http://localhost:8000](http://localhost:8000)

### Manage
If you need to interact with `manage.py`, you can use `inv manage <cmd>` where `<cmd>` is the management command you wish to run. If you need to pass flags as well, put your command in quotes, i.e. `inv manage 'flush --noinput'`.

**Note**: Running commands that require input is a quite dodgy, so commands like `shell` and `dbshell` only display input when pressing enter.

### CSS
Djangit uses Bootstrap and Font Awesome for a beautiful look.

Thus all styles are written in SASS and need to be compiled into CSS. Run this
command in the root directory to compile it:

    inv css
