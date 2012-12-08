Summary:	The sound scripts
Name:		sound-scripts
Version:	0.62
Release:	4
License:	GPLv2+
Url:		http://svn.mandriva.com/viewvc/soft/sound-scripts/
Group:		System/Base
Source0:	%{name}-%{version}.tar.xz
Patch1: sound-scripts-0.62-fix-lsb-init.patch
Patch2: sound-scripts-0.62-fix-oss-emulation-for-kmod.patch
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

# (cg) alsa-utils has native support for sustemd that totally overrides
# all the volume save/restoration features of this package. In order to
# allow for use of sysvinit for now, we simply mask the services under systemd
mkdir -p %{buildroot}%{_unitdir}
rm -f %{buildroot}%{_unitdir}/{alsa,sound}.service
ln -s /dev/null %{buildroot}%{_unitdir}/sound.service
ln -s /dev/null %{buildroot}%{_unitdir}/alsa.service

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

%post
%_post_service sound
%_post_service alsa

%preun
%_preun_service sound
%_preun_service alsa

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
%{_initrddir}/*
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/udev/rules.d/*
#config(noreplace) %{_sysconfdir}/modprobe.d/snd-usb-audio.conf
%config(noreplace) %{_sysconfdir}/modprobe.d/snd-oss.conf
%{_datadir}/alsa/alsa-utils
/lib/systemd/system/alsa.service
/lib/systemd/system/sound.service


%changelog
* Mon Oct 15 2012 akdengi <akdengi> 0.62-4
- Rebuild with new spec-helper for non-relative symlnks to /dev/null
- require kmod instead of module-init-tools

* Fri Jan 06 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.62-2
+ Revision: 758265
- fix dependency on rpm-helper to be Requires(post,preun):
- fix executable-marked-as-config-file
- update license tag (GPL -> GPLv2+)
- don't own %%{_datadir}/alsa
- update url
- clean out redundant dependencies
- drop ancient conflicts
- apply some cosmetics
- drop legacy rpm stuff
- add '.conf' suffix to modprobe conf files

* Wed Nov 02 2011 Alexander Barakin <abarakin@mandriva.org> 0.61-2
+ Revision: 711976
- change path to asound.state file. (#64134)

* Wed May 25 2011 Eugeni Dodonov <eugeni@mandriva.com> 0.61-1
+ Revision: 679082
- 0.61:
- prevent hang on shutdown/reboot caused by fuser being too greedy
- systemd integration

* Fri May 06 2011 Oden Eriksson <oeriksson@mandriva.com> 0.60-4
+ Revision: 669999
- mass rebuild

* Tue Jan 25 2011 Eugeni Dodonov <eugeni@mandriva.com> 0.60-3
+ Revision: 632501
- Added systemd units.
  Switched back to _post_service for service setup.

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 0.60-2mdv2011.0
+ Revision: 607549
- rebuild

* Wed Feb 10 2010 Frederik Himpe <fhimpe@mandriva.org> 0.60-1mdv2010.1
+ Revision: 504004
- Release 0.60:
 - sound service:
   o use a secure file in default tmp directory (#55929) (Thierry
     Vignaud)
 - alsa_default.pl:
   o kernel 2.6.33 renamed 'PC Beep' into 'Beep' (#57320); support both
     (Andrey Borzenkov)

* Fri Oct 02 2009 Frederic Crozat <fcrozat@mandriva.com> 0.59-1mdv2010.0
+ Revision: 452643
- Release 0.59 :
 - do not save alsa levels at shutdown, done in halt now

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 0.58-2mdv2010.0
+ Revision: 427204
- rebuild

* Tue Apr 07 2009 Thierry Vignaud <tv@mandriva.org> 0.58-1mdv2009.1
+ Revision: 364829
- alsa_default.pl:
  o reduce level of speaker to 20%% (#49045)

* Mon Mar 02 2009 Frederik Himpe <fhimpe@mandriva.org> 0.57-1mdv2009.1
+ Revision: 347509
- Release 0.57:
- alsa_default.pl: mute Audigy Analog/Digital Output Jack by default (not
  a straightforward issue, see comment) (Adam Williamson)
- alsa_default.pl: disable PC Beep by default (#45386)

* Fri Oct 24 2008 Adam Williamson <awilliamson@mandriva.org> 0.56-1mdv2009.1
+ Revision: 296977
- new release 0.56: mute Analog Loopback by default (#44703)

* Mon Sep 22 2008 Frederic Crozat <fcrozat@mandriva.com> 0.55-1mdv2009.0
+ Revision: 286670
- Release 0.55 :
  - don't try to unload modules at shutdown / reboot
  - use modprobe.d file to load oss compat modules, not alsa service
  - remove useless sleep at shutdown for alsa
  - remove call to deprecated alsactl command

* Mon Sep 15 2008 Thierry Vignaud <tv@mandriva.org> 0.54-1mdv2009.0
+ Revision: 284867
- alsa initscript:
  o adapt to latest udev (#43828)

* Wed Jun 18 2008 Thierry Vignaud <tv@mandriva.org> 0.53-2mdv2009.0
+ Revision: 225450
- rebuild

* Fri Apr 04 2008 Olivier Blin <blino@mandriva.org> 0.53-1mdv2008.1
+ Revision: 192313
- 0.53
- fix loading snd-usb-audio (#34613)

* Thu Apr 03 2008 Thierry Vignaud <tv@mandriva.org> 0.52-1mdv2008.1
+ Revision: 192025
- alsa initscript:
  o fix matching snd-usb-audio devices (#36466)

* Tue Mar 25 2008 Thierry Vignaud <tv@mandriva.org> 0.51-1mdv2008.1
+ Revision: 190089
- alsa initscript:
  o load snd-usb-audio for devices of "audio" Class and of subclass 3
    too (#39376)

* Fri Mar 14 2008 Thierry Vignaud <tv@mandriva.org> 0.50-3mdv2008.1
+ Revision: 187935
- remove requires on /usr/bin/tr (part of coreutils)

* Wed Mar 12 2008 Thierry Vignaud <tv@mandriva.org> 0.50-2mdv2008.1
+ Revision: 187112
- enable to restore sound level after stoping the service
  (Christophe Gaubert, #38038)

* Wed Mar 05 2008 Oden Eriksson <oeriksson@mandriva.com> 0.49-2mdv2008.1
+ Revision: 179513
- rebuild

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Wed Sep 12 2007 Olivier Blin <blino@mandriva.org> 0.49-1mdv2008.0
+ Revision: 84588
- add /etc/modprobe.d/snd-usb-audio to prevent snd-usb-audio loading when alsa service is not started

* Tue Sep 04 2007 Thierry Vignaud <tv@mandriva.org> 0.48-1mdv2008.0
+ Revision: 79373
- load OSS compat modules if they'ven't be loaded through /etc/modprobe.conf

* Mon Sep 03 2007 Thierry Vignaud <tv@mandriva.org> 0.47-1mdv2008.0
+ Revision: 78501
- restore mixer even if we already load OSS compat modules through
  /etc/modprobe.conf (ie if draksound was used in order to reconfigure the
  sound card) (#29071)

* Fri Aug 31 2007 Thierry Vignaud <tv@mandriva.org> 0.46-1mdv2008.0
+ Revision: 76981
- call udevsettle so that services waiting for alsa service to
  complete see devices created (#20761)
- fix loading OSS compat modules on restart (#21246)
- fix some test due to [_-] changes in module names
- do load the OSS compat modules & restore sound level even if udev already
  load the module through PCI coldplug (#32994)

* Thu May 03 2007 Thierry Vignaud <tv@mandriva.org> 0.44-2mdv2008.0
+ Revision: 21813
- adjust file list
- bump release
- bump require on alsa-utils because of /usr/sbin -> /sbin move
- run reset_sound and alsactl from root fs rather than /usr (#30368)
- Import sound-scripts




* Tue Sep 19 2006 Olivier Blin <oblin@mandriva.com> 0.43-1mdv2007.0
- reenable snd-usb-audio at service start only, not during stop (#12731)

* Thu May 11 2006 Thierry Vignaud <tvignaud@mandriva.com> 0.42-1mdk
- on startup, generate /etc/asound.names if needed

* Thu Apr 13 2006 Thierry Vignaud <tvignaud@mandriva.com> 0.41-1mdk
- alsa service:
  o fix perms on resuming after suspending (#21925)
  o silent stop (J.A. Magallon)
- reset_sound:
  o fix playing sound on Hercules Gamesurround Fortissimo 4 (#21173)
  o try fixing playing sound on SB Audigy 2 (#18735)

* Sat Jan 28 2006 Thierry Vignaud <tvignaud@mandriva.com> 0.40-1mdk
- fix restoring mixer (#20873)

* Tue Jan 17 2006 Thierry Vignaud <tvignaud@mandriva.com> 0.39-1mdk
- fix restoring mixer when not using udev (#20636)

* Mon Jan  9 2006 Olivier Blin <oblin@mandriva.com> 0.38-1mdk
- convert parallel init to LSB
- the sound service should start the alsa service

* Mon Jan  2 2006 Olivier Blin <oblin@mandriva.com> 0.37-1mdk
- add parallel init support

* Thu Dec 15 2005 Thierry Vignaud <tvignaud@mandriva.com> 0.36-1mdk
- adapt to new udev (#20175)

* Fri Sep 16 2005 Thierry Vignaud <tvignaud@mandriva.com> 0.35-1mdk
- use new aumix-text instead of aumix

* Thu Sep 15 2005 Thierry Vignaud <tvignaud@mandriva.com> 0.34-1mdk
- fix recording on Via FX41/VT8233 && ATI IXP400 (#14571)

* Sun Sep 11 2005 Thierry Vignaud <tvignaud@mandriva.com> 0.33-1mdk
- requires aumix (#18397)

* Fri Sep  9 2005 Thierry Vignaud <tvignaud@mandriva.com> 0.32-1mdk
- supress harmless error message (#18394)

* Wed Sep  7 2005 Thierry Vignaud <tvignaud@mandriva.com> 0.31-1mdk
- alsa service: unblacklist audio too (#12731)

* Tue Sep  6 2005 Thierry Vignaud <tvignaud@mandriva.com> 0.30-1mdk
- fix sound on Creative Labs EMU10K2: most users use analog HPs rather
  than digital ones (#18235)

* Fri Aug 19 2005 Thierry Vignaud <tvignaud@mandriva.com> 0.29-1mdk
- alsa service:
 o ensure we don't accumulates empty lines in /etc/hotplug/blacklist
 o use the new way to disable blacklisting modules (#12731)

* Thu Aug 11 2005 Flavio Bruno Leitner <flavio@mandriva.com> 0.28-2mdk
- changed requires from modutils to module-init-tools

* Mon Aug  8 2005 Thierry Vignaud <tvignaud@mandriva.com> 0.28-1mdk
- fix saving sound level

* Mon Aug 08 2005 Thierry Vignaud <tvignaud@mandriva.com> 0.27-1mdk
- move from dev.d to event handler only answering to proper events

* Thu Jul  7 2005 Thierry Vignaud <tvignaud@mandriva.com> 0.26-1mdk
- enable "External Amplifier" (fix sound on new laptops, #16582)

* Wed Mar 30 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.25-1mdk
- fix sound on SB Audigy LS

* Fri Mar 25 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.24-1mdk
- fix alsa mixer restoring on boot (#14967)

* Tue Mar  8 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.23-1mdk
- move udev event handler (really fixing multiple cards support - #13103)

* Mon Mar  7 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.22-1mdk
- fix multiple card support (#13103)
- fix reseting sound volume on udev update

* Fri Mar  4 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.21-1mdk
- really fix #13911

* Mon Feb 28 2005  <tv@vador.mandrakesoft.com> 0.20-1mdk
- filter out error messages when USB subsystem is not availlable (#13977)
- fix distortion on SBLive Value with stereo analogue speakers (#13911)
- fix low sound on some laptops with internal HPs

* Fri Feb 11 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.19-1mdk
- better support for partially statically compiled ALSA

* Fri Feb 11 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.18-1mdk
- typo fix (#13504), thus really fixing #12731

* Wed Feb  9 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.17-1mdk
- alsa service: better check to know whether ALSA drivers are loaded
  or not (fix broken sound startup when a webcam is plugged, #12731)
- fix alsa mixer restore when not using udev

* Tue Feb  1 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.16-1mdk
- fix no PID of programs using alsa shown when stopping alsa (#13102)
- handle multiple sound cards (#13103)

* Wed Jan 19 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.15-1mdk
- alsa_default.pl:
  o fix broken blacklisting (broken since 0.09-1mdk)
  o fix sound on i845 with ALSA-1.0.8+
  o remute blacklisted entries if manually unmuted by the user
- udev event handler: save sound level on ALSA shutdown and on udev
  shutdown (eg: gently handle udev update so that the mixer doesn't
  suddendly got reseted to boot's defaults because the user hasn't
  save them)

* Wed Jan 12 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.14-1mdk
- fix alsactl path (#12986)

* Tue Jan 11 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.13-1mdk
- smooth startup when using udev (ALSA levels are now restored
  asynchronously)
- display FAILED if restoring mixer levels failed
- factorize ALSA mixer restoring into /etc/dev.d/snd/controlC0/alsa.dev

* Tue Jan  4 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.12-1mdk
- wait_for_sysfs is dead

* Sun Dec  5 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.11-1mdk
- use wait_for_sysfs in order to speed up starting time

* Fri Dec  3 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.10-1mdk
- fix udev check after switching from udev-030 to udev-046 (#12553)

* Thu Nov  4 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.09-1mdk
- alsa_default.pl:
  o fix too fast sound on "Terratec Aureon 5.1 Sky" (#12100)
  o documment each blacklisted mixer element
  o generalize SB Live fix so that it works on Audigy too (both EMU10K
    and EMU10K2) (#7938)
- reset_sound: make it work for non root users too

* Tue Nov  2 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.08-1mdk
- be more robust when parsing asound.state (thus fixing support for
  the Turtle Beach Santa Cruz soundcard, which uses the Cirrus Logic
  CS4297A driver (#12151))

* Fri Oct  1 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.07-1mdk
- alsa service: load snd audio if needed (because snd-usb-audio is now
  blacklisted on early boot and reenable USB sound audio hotplugging
  (for later (un-)plugging) (#8004)
- fix loud sound on cmpci cards

* Fri Sep 10 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.06-1mdk
- enforce proper package ordering when updating from mdk10.0 + updates
- workaround udev slowly creating /dev/ nodes on module load (Luca Berra)
- when mixer elements were altered (aka on kernel switches), run
  reset_sound like we do on first boot

* Thu Sep  9 2004 Frederic Lepied <flepied@mandrakesoft.com> 0.05-1mdk
- noarch
- prereq rpm-helper
- use alsactl -F restore to be more safe

* Fri Jun  4 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.04-1mdk
- add reset_sound in order to reinitialize sound level to the first
  boot one

* Fri Jun  4 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.03-1mdk
- fix larsen on laptops with ALI chipsets

* Fri May 28 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.02-1mdk
- fix larsen on some DELL notebooks (with i8xx chipsets)

* Wed Mar 24 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.01-1mdk
- new package, splited from initscripts
