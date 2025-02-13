#!/usr/share/ucs-test/runner python3
## desc: Create and install a simple docker app and check ports exclusive
## tags: [docker]
## exposure: dangerous
## packages:
##   - docker.io

from textwrap import dedent

from univention.testing.utils import is_port_open, restart_firewall

from dockertest import App, Appcenter, get_app_name, get_app_version, get_docker_appbox_image, get_docker_appbox_ucs


if __name__ == '__main__':
    with Appcenter() as appcenter:

        app_name = get_app_name()
        app_version = get_app_version()
        app = App(name=app_name, version=app_version, container_version=get_docker_appbox_ucs(), build_package=False)
        ports = ['21', '23']
        packages = ['telnetd', 'proftpd']
        image = get_docker_appbox_image()

        # check ports are unused
        for port in ports:
            assert not is_port_open(port)

        try:
            # check ports exclusive
            app.set_ini_parameter(
                DockerImage=image,
                PortsExclusive=','.join(ports),
                DefaultPackages=','.join(packages),
                DockerScriptSetup='/usr/sbin/%s-setup' % app_name)
            app.add_script(setup=dedent('''\
                #!/bin/bash
                set -x -e
                ucr set repository/online/unmaintained='yes'
                univention-app update
                univention-app register "%(app_name)s" --component
                app_packages="$(univention-app get "%(app_name)s" default_packages --values-only --shell)"
                univention-install -y $app_packages
                ''') % {'app_name': app_name})
            app.add_to_local_appcenter()
            appcenter.update()
            app.install()

            # check ports are open
            for port in ports:
                assert is_port_open(port)

            # restart firewall and check again
            restart_firewall()

            # check ports are open
            for port in ports:
                assert is_port_open(port)
        finally:
            app.uninstall()
            app.remove()

        # check ports are unused
        for port in ports:
            assert not is_port_open(port)
