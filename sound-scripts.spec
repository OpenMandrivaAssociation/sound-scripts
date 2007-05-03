# 	$Id: sound-scripts.spec 62275 2006-09-18 22:32:24Z blino $	
# EDIT IN CVS NOT IN SOURCE PACKAGE (NO PATCH ALLOWED).

# The following macro were stolen from initscripts spec file:
# The restart part in the real _post_service doesn't work with netfs and isn't needed
# for other scripts
%define _mypost_service() if [ $1 = 1 ]; then /sbin/chkconfig --add %{1}; fi;
%define initlvl_chg() if [[ -f /etc/rc3.d/S%{2}%{1} ]] && [[ -f /etc/rc5.d/S%{2}%{1} ]] && egrep -q 'chkconfig: [0-9]+ %{3}' /etc/init.d/%{1}; then chkconfig --add %{1} || : ; fi; \
%{nil}

Summary: The sound scripts
Name: sound-scripts
Version: 0.44
Release: %mkrel 1
License: GPL
Url: http://www.mandrivalinux.com/cgi-bin/cvsweb.cgi/soft/sound-scripts/
Group: System/Base
Source0: %name-%version.tar.bz2
BuildRoot: %_tmppath/%name-root
BuildArch: noarch
Requires: procps >= 2.0.7-8mdk, module-init-tools, aumix-text
Requires(Pre): chkconfig >= 1.3.8-3mdk, coreutils, /usr/bin/tr, grep, rpm-helper
Conflicts: initscripts <= 7.06-50mdk
Conflicts: alsa-utils <= 1.0.14-1.rc4
Conflicts: udev < 0.50-5mdk

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
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/etc
%makeinstall_std

# there's no interesting string that is already gprintified
export DONT_GPRINTIFY=1


%post
%_mypost_service sound
%_mypost_service alsa

# only needed on upgrade
if [ $1 != 0 ]; then
	# Handle boot sequence changes on upgrade
	%initlvl_chg sound 71 18
	%initlvl_chg alsa 70 17
fi

%preun
%_preun_service sound
%_preun_service alsa

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc ChangeLog
%_bindir/reset_sound
%_sbindir/alsa.agent
%config(noreplace) /etc/rc.d/rc.alsa_default
%config(noreplace) /etc/sysconfig/alsa
/etc/rc.d/init.d/*
%config(noreplace) %attr(0644,root,root) /%{_sysconfdir}/udev/rules.d/*
%_datadir/alsa/
