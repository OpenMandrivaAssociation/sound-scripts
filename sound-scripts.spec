Summary:	The sound scripts
Name:		sound-scripts
Version:	0.62
Release:	18
License:	GPLv2+
Url:		http://svn.mandriva.com/viewvc/soft/sound-scripts/
Group:		System/Base
Source0:	%{name}-%{version}.tar.xz
Patch1:		sound-scripts-0.62-fix-lsb-init.patch
Patch2:		sound-scripts-0.62-fix-oss-emulation-for-kmod.patch
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
%apply_patches

%build
make

%install
%makeinstall_std

# there's no interesting string that is already gprintified
export DONT_GPRINTIFY=1

# (tpg) we don't need this anymore
rm -rf %{buildroot}%{_unitdir}/*.service
rm -rf %{buildroot}%{_initrddir}

# (tpg) move rules to proper place
mkdir -p %{buildroot}/lib/
mv %{buildroot}%{_sysconfdir}/udev %{buildroot}/lib/

# (cg) The modprobe tweaks to snd-usb-audio prevents it from loading
# unless the sysvinit scritps are loaded. This is incorrect as when
# using systemd, the sysvinit scripts are not used (instead the upstream
# solution to save/restore volume from alsa-utils package is used)
rm -f %{buildroot}%{_sysconfdir}/modprobe.d/snd-usb-audio.conf

# (cg) Move the OSS config into sound profiles so we can easily
# use osspd with PulseAudio by default
mkdir -p %{buildroot}%{_sysconfdir}/sound/profiles/{alsa,pulse}
mv %{buildroot}%{_sysconfdir}/modprobe.d/snd-oss.conf %{buildroot}%{_sysconfdir}/sound/profiles/alsa
ln -sf %{_sysconfdir}/sound/profiles/current/snd-oss.conf %{buildroot}%{_sysconfdir}/modprobe.d/snd-oss.conf
cat >%{buildroot}%{_sysconfdir}/sound/profiles/pulse/snd-oss.conf <<EOF
# We need to ensure that no ALSA OSS compatibility modules are loaded so
# we can use osspd easily
blacklist snd_pcm_oss
blacklist snd_mixer_oss
blacklist snd_seq_oss
EOF

%pre
if [ -e /etc/modprobe.d/snd-oss ]; then
	mv /etc/modprobe.d/snd-oss{,.conf}
fi

%files
%doc ChangeLog
%{_bindir}/reset_sound
/bin/reset_sound
%{_sbindir}/alsa.agent
/sbin/alsa.agent
%{_sysconfdir}/rc.d/rc.alsa_default
%{_sysconfdir}/sound/profiles/alsa/snd-oss.conf
%{_sysconfdir}/sound/profiles/pulse/snd-oss.conf
%config(noreplace) %{_sysconfdir}/sysconfig/alsa
%config(noreplace) %attr(0644,root,root) /lib/udev/rules.d/*
#config(noreplace) %{_sysconfdir}/modprobe.d/snd-usb-audio.conf
%config(noreplace) %{_sysconfdir}/modprobe.d/snd-oss.conf
%{_datadir}/alsa/alsa-utils
