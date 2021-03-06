%define pkg_parent skyring-core

Name: skynet
Version: @VERSION@
Release: 1%{?dist}
BuildArch: noarch
Summary: SKYRING Node Event Agent
Source0: %{name}-%{version}.tar.gz
License: ASL 2.0
Group: Development/Libraries
Url: https://github.com/skyrings/skynet

BuildRequires: python-devel
BuildRequires: python-setuptools

Requires: collectd
Requires: collectd-ping
Requires: python-cpopen
Requires: python-setuptools
Requires: salt-minion >= 2015.5.5
Requires: storaged
Requires: storaged-lvm2
Requires: socat
Requires: bc
Requires: salt-selinux
Requires: %{pkg_parent}-selinux

%description
SKYNET is the event agent for SKYRING. Each storage node managed
by SKYRING will have this agent running on them. It is a daemon which listens
to DBUS signals, filters it, processes it and pushes the filtered signals to
SKYRING using salt-stack event framework. Currently this daemon has
capability to send basic storage, process and network related events.

%prep
%setup

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
install -Dm 0644 conf/skynet_logrotate.conf.sample $RPM_BUILD_ROOT/etc/logrotate.d/skynet
install -Dm 0644 conf/skynet-sudoers.conf $RPM_BUILD_ROOT/%{_sysconfdir}/sudoers.d/skynet-sudoers
install -Dm 0644 src/skynetd/conf/skynet.conf.sample $RPM_BUILD_ROOT/etc/skynet/skynet.conf
install -Dm 0644 src/skynetd/conf/skynet-log.conf.sample $RPM_BUILD_ROOT/etc/skynet/skynet-log.conf
install -Dm 0644 skynetd.service $RPM_BUILD_ROOT/usr/lib/systemd/system/skynetd.service
install -D src/collectd_scripts/handle_collectd_notification.py $RPM_BUILD_ROOT/usr/lib64/collectd/handle_collectd_notification.py
install -Dm 0755 src/collectd_scripts/ifspeed.sh $RPM_BUILD_ROOT/usr/lib64/collectd/ifspeed.sh
gzip skynetd.8
install -Dm 0644 skynetd.8.gz $RPM_BUILD_ROOT%{_mandir}/man8/skynetd.8.gz
chmod a+x $RPM_BUILD_ROOT%{python_sitelib}/skynetd/skynetd.py

%pre
if [ `grep -c ^skyring-user /etc/passwd` = "0" ]; then
    /usr/sbin/useradd skyring-user -g wheel
fi


%post
dbus-send --system --print-reply --type=method_call --dest=org.storaged.Storaged /org/storaged/Storaged/Manager org.storaged.Storaged.Manager.EnableModules boolean:true
/bin/systemctl enable skynetd.service >/dev/null 2>&1 || :
/bin/systemctl restart skynetd.service >/dev/null 2>&1 || :

%files -f INSTALLED_FILES
%{_sysconfdir}/skynet/
%{_sysconfdir}/logrotate.d/skynet
%{_sysconfdir}/sudoers.d/skynet-sudoers
%config(noreplace) %{_sysconfdir}/skynet/skynet.conf
%config(noreplace) %{_sysconfdir}/skynet/skynet-log.conf
%{_usr}/lib/systemd/system/skynetd.service
%{_usr}/lib64/collectd/
%doc README.md
%{_mandir}/man8/skynetd.8*

%changelog
* Thu Dec 03 2015 Timothy Asir Jeyasingh <tjeyasin@redhat.com> - 0.0.1-1
- Initial build.
