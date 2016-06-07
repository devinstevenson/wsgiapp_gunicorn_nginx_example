from fabric.api import env, run, settings, sudo, put, cd

env.use_ssh_config = True
# env.hosts = ['amd1', 'amd2']
# env.shell = "/bin/bash -l -i -c"

def setup_wsgi():
    with settings(warn_only=True):
        make_nginx_conf()
        run("mkdir -p /home/amd1/github/wsgiapp")
        put("wsgiapp", "/home/amd1/github")
        put("requirements.txt", "/home/amd1/github/wsgiapp/requirements.txt")
        with cd("/home/amd1/github/wsgiapp"):
            run("/home/amd1/miniconda2/bin/pip install -r requirements.txt")

        put("wsgiapp.conf", "/etc/init/wsgiapp.conf", use_sudo=True)
        put("wsgiapp_nginx", "/etc/nginx/sites-available/wsgiapp_nginx", use_sudo=True)

        sudo("rm -rf /etc/nginx/sites-enabled/default")
        sudo("ln -s /etc/nginx/sites-available/wsgiapp_nginx /etc/nginx/sites-enabled")
        sudo("start wsgiapp")
        run("ps aux | grep wsgiapp")
        sudo("service nginx restart")

def cleanup():
    with settings(warn_only=True):
        sudo("stop wsgiapp")
        run("rm -rf /home/amd1/github/wsgiapp")
        sudo("rm -rf /etc/init/wsgiapp.conf")
        sudo("rm -rf /etc/nginx/sites-enabled/wsgiapp_nginx")
        sudo("rm -rf /etc/nginx/sites-available/wsgiapp_nginx")
        sudo("ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled")
        sudo("service nginx restart")
        run("ps aux | grep wsgiapp")

def make_nginx_conf():
    conf = ['server {',
            '    listen 80;',
            '    server_name {0};'.format(env['host']),
            '',
            '    location / {',
            '        include       uwsgi_params;',
            '        uwsgi_pass    unix:/home/amd1/github/wsgiapp/wsgiapp.sock;',
            '    }',
            '}']
    with open('wsgiapp_nginx', 'wb') as f:
        for i in conf:
            f.write(i)
            f.write('\n')
