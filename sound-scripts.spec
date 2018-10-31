Summary:	The sound scripts
Name:		sound-scripts
Version:	0.62.1
Release:	2
License:	GPLv2+
Url:		https://github.com/OpenMandrivaSoftware/sound-scripts
Group:		System/Base
Source0:	%{name}-%{version}.tar.xz
BuildArch:	noarch
Requires:	aumix-text
Requires:	kmod
Requires:	alsa-utils >= 1.0.25
Requires(post,preun):	rpm-helper

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
%makeinstall_std

# there's no interesting string that is already gprintified
export DONT_GPRINTIFY=1

%pre
if [ -e /etc/modprobe.d/snd-oss ]; then
    mv /etc/modprobe.d/snd-oss{,.conf}
fi

%files
%doc ChangeLog
%{_bindir}/reset_sound
%{_sbindir}/alsa.agent
%{_sysconfdir}/rc.d/rc.alsa_default
%{_sysconfdir}/sound/profiles/alsa/snd-oss.conf
%{_sysconfdir}/sound/profiles/pulse/snd-oss.conf
%config(noreplace) %{_sysconfdir}/sysconfig/alsa
%config(noreplace) %attr(0644,root,root) /lib/udev/rules.d/*
%config(noreplace) %{_sysconfdir}/modprobe.d/snd-oss.conf
%{_datadir}/alsa/alsa-utils
