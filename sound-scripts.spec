Summary: The sound scripts
Name: sound-scripts
Version: 0.62
Release: 1
License: GPL
Url: http://www.mandrivalinux.com/cgi-bin/cvsweb.cgi/soft/sound-scripts/
Group: System/Base
Source0: %name-%version.tar.xz
BuildArch: noarch
Requires: procps >= 2.0.7-8mdk, module-init-tools, aumix-text
Requires(Pre): chkconfig >= 1.3.8-3mdk, coreutils, grep, rpm-helper
Conflicts: initscripts <= 7.06-50mdk
Conflicts: alsa-utils <= 1.0.14-1.rc4
Conflicts: udev < 0.50-5mdk
Conflicts: harddrake < 10.4.191-1mdv2008.0

%description
The sound-scripts package contains the basic system scripts used:
- to setup default sound mixer on first boot
- save sound mixer level on shutdown
- restore sound mixer on bootstrapping

%prep
%setup -q

%build
make

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%makeinstall_std

# there's no interesting string that is already gprintified
export DONT_GPRINTIFY=1


%post
%_post_service sound
%_post_service alsa

%preun
%_preun_service sound
%_preun_service alsa

%files
%doc ChangeLog
%_bindir/reset_sound
/bin/reset_sound
%_sbindir/alsa.agent
/sbin/alsa.agent
%config(noreplace) /etc/rc.d/rc.alsa_default
%config(noreplace) /etc/sysconfig/alsa
/etc/rc.d/init.d/*
%config(noreplace) %attr(0644,root,root) /%{_sysconfdir}/udev/rules.d/*
%config(noreplace) /etc/modprobe.d/snd-usb-audio.conf
%config(noreplace) /etc/modprobe.d/snd-oss.conf
%_datadir/alsa/
/lib/systemd/system/alsa.service
/lib/systemd/system/sound.service
