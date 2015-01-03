from __future__ import with_statement
from fabric.api import *  # noqa

env.app = 'finance'
env.hosts = ['web1']
env.sites_dir = '/opt/sites/'
env.app_dir = env.sites_dir + env.app
env.repo = "http://git.ironlabs.com/greg/finance.git"
env.nginx_conf_dir = "/opt/nginx/conf/sites/"
env.uwsgi_conf_dir = "/etc/uwsgi/apps/"
env.user = 'root'
env.key_filename = '/home/greg/.ssh/id_digitalocean'

USE_DB = True


def install_requirements():
    run("source {0}/bin/activate && "
        "pip install -r requirements/install.txt".format(env.app_dir))


def setup_nginx():
    run("cp {app_dir}/master/nginx.conf {nginx_conf_dir}{app}.conf".format(
        app_dir=env.app_dir,
        nginx_conf_dir=env.nginx_conf_dir,
        app=env.app
    ))


def setup_uwsgi():
    run("cp {app_dir}/master/uwsgi.ini {uwsgi_conf_dir}{app}.ini".format(
        app_dir=env.app_dir,
        uwsgi_conf_dir=env.uwsgi_conf_dir,
        app=env.app
    ))


def setup_logdir():
    with settings(user="root"):
        with cd(env.app_dir):
            run("mkdir logs")
            run("touch logs/debug.log")
            run("chown -R uwsgi:uwsgi logs")


def update_db():
    run("source {0}/bin/activate &&"
        " python manage.py migrate".format(env.app_dir))


def set_staticfiles():
    run("source {0}/bin/activate &&"
        " python manage.py collectstatic -v0 --noinput".format(env.app_dir))


def install():
    """Installs app on server"""
    with settings(user="root"):
        run("virtualenv -p python2 {app_dir}".format(
            app_dir=env.app_dir
        ))
        with cd(env.app_dir):
            run("git clone {repo} master".format(repo=env.repo))
            with cd("master"):
                install_requirements()
                setup_nginx()
                setup_uwsgi()
        setup_logdir()
    print("Setup environment variables and then do an update.")


def update():
    """Updates code base on server"""
    with settings(user="root"):
        with cd("{app_dir}/master".format(app_dir=env.app_dir)):
            run("git pull")
            install_requirements()
            # setup_nginx()
            # setup_uwsgi()
            if USE_DB:
                update_db()
            set_staticfiles()
        run("systemctl reload emperor.uwsgi")
        run("systemctl reload nginx")
