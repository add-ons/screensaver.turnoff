import atexit
import subprocess
import sys

import xbmc
import xbmcaddon
import xbmcgui


def log_error(msg='', level=xbmc.LOGERROR):
    xbmc.log(msg='[%s] %s' % (addon_id, msg), level=level)


def log_info(msg='', level=xbmc.LOGINFO):
    xbmc.log(msg='[%s] %s' % (addon_id, msg), level=level)


def log_notice(msg='', level=xbmc.LOGNOTICE):
    xbmc.log(msg='[%s] %s' % (addon_id, msg), level=level)


def popup(heading='', msg='', delay=10000, icon=''):
    if not heading:
        heading = 'Addon %s failed' % addon_id
    if not icon:
        icon = addon_icon
    xbmcgui.Dialog().notification(heading, msg, icon, delay)


def set_mute(toggle=True):
    payload = '{"jsonrpc": "2.0", "method": "Application.SetMute", "params": {"mute": %s}}' % ('true' if toggle else 'false')
    result = xbmc.executeJSONRPC(payload)
    log_info(msg="Sending JSON-RPC payload: '%s' returns '%s'" % (payload, result))


def run_builtin(builtin):
    log_info(msg="Executing builtin '%s'" % builtin)
    try:
        xbmc.executebuiltin(builtin)
    except Exception as e:
        log_error(msg="Exception executing builtin '%s': %s" % (builtin, e))
        popup(msg="Exception executing builtin '%s': %s" % (builtin, e))


def run_command(command, shell=False):
    # TODO: Add options for running using su or sudo
    try:
        cmd = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell)
        (out, err) = cmd.communicate()
        if cmd.returncode == 0:
            log_notice(msg="Running command '%s' returned rc=%s" % (' '.join(command), cmd.returncode))
        else:
            log_error(msg="Running command '%s' failed with rc=%s" % (' '.join(command), cmd.returncode))
            if err:
                log_error(msg="Command '%s' returned on stderr: %s" % (command[0], err))
            if out:
                log_error(msg="Command '%s' returned on stdout: %s " % (command[0], out))
            popup(msg="%s\n%s" % (out, err))
            sys.exit(1)
    except Exception as e:
        log_error(msg="Exception running '%s': %s" % (command[0], e))
        popup(msg="Exception running '%s': %s" % (command[0], e))
        sys.exit(2)


class TurnOffMonitor(xbmc.Monitor):

    def __init__(self, *args, **kwargs):
        self.action = kwargs['action']

    def onScreensaverDeactivated(self):
        self.action()


class TurnOffScreensaver(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        pass

    def onInit(self):
        self._monitor = TurnOffMonitor(self.exit)

        # Turn off display
        if display_method != 0:
            log_notice(msg='Turn display signal off using method %s' % display_method)

        if display_method == '1':  # CEC (built-in)
            run_builtin('CECStandby')
        elif display_method == '2':  # No Signal on Raspberry Pi (using vcgencmd)
            run_command(['vcgencmd', 'display_power', '0'])
        elif display_method == '3':  # DPMS (built-in)
            run_builtin('ToggleDPMS')
        elif display_method == '4':  # DPMS (using xset)
            run_command(['xset', 'dpms', 'force', 'off'])
        elif display_method == '5':  # DPMS (using vbetool)
            run_command(['vbetool', 'dpms', 'off'])
        elif display_method == '6':  # DPMS (using xrandr)
            # NOTE: This needs more outside testing
            run_command(['xrandr', '--output CRT-0', 'off'])
        elif display_method == '7':  # CEC on Android (kernel)
            # NOTE: This needs more outside testing
            run_command(['su', '-c', 'echo 0 >/sys/devices/virtual/graphics/fb0/cec'], shell=True)
        elif display_method == '8':  # Backlight on Raspberry Pi (kernel)
            # NOTE: Contrary to what you might think, 1 means off
            run_command(['su', '-c', 'echo 1 >/sys/class/backlight/rpi_backlight/bl_power'], shell=True)

        # FIXME: Screensaver always seems to lock when started, requires unlock and re-login
        # Log off user
        if logoff == 'true':
            run_builtin('System.Logoff()')

        # Mute audio
        if mute == 'true':
            log_notice(msg='Mute audio')
            set_mute(True)
            # NOTE: Since the Mute-builtin is a toggle, we need to do this to ensure Mute
#            run_builtin('VolumeDown')
#            run_builtin('Mute')

        # Power off system
        if power_method != 0:
            log_notice(msg='Turn system off using method %s' % power_method)
        if power_method == '1':  # Suspend (built-in)
            run_builtin('Suspend')
        elif power_method == '2':  # Hibernate (built-in)
            run_builtin('Hibernate')
        elif power_method == '3':  # Quit (built-in)
            run_builtin('Quit')
        elif power_method == '4':  # ShutDown action (built-in)
            run_builtin('ShutDown')
        elif power_method == '5':  # Reboot (built-in)
            run_builtin('Reboot')
        elif power_method == '6':  # PowerDown (built-in)
            run_builtin('PowerDown')
        elif power_method == '7':  # Android POWER key event (using input)
            run_command(['su', '-c', 'input keyevent KEYCODE_POWER'], shell=True)

    def resume(self):
        # Unmute audio
        if mute == 'true':
            log_notice(msg='Unmute audio')
            set_mute(False)
#            run_builtin('Mute')
            # NOTE: Since the Mute-builtin is a toggle, we need to do this to ensure Unmute
#            run_builtin('VolumeUp')

        # Turn on display
        if display_method != 0:
            log_notice(msg='Turn display signal back on using method %s' % display_method)
        if display_method == '1':  # CEC (built-in)
            run_builtin('CECActivateSource')
        elif display_method == '2':  # No Signal on Raspberry Pi (using vcgencmd)
            run_command(['vcgencmd', 'display_power', '1'])
        elif display_method == '3':  # DPMS (built-in)
            run_builtin('ToggleDPMS')
        elif display_method == '4':  # DPMS (using xset)
            run_command(['xset', 'dpms', 'force', 'on'])
        elif display_method == '5':  # DPMS (using vbetool)
            run_command(['vbetool', 'dpms', 'on'])
        elif display_method == '6':  # DPMS (using xrandr)
            # NOTE: This needs more outside testing
            run_command(['xrandr', '--output CRT-0', 'on'])
        elif display_method == '7':  # CEC on Android (kernel)
            # NOTE: This needs more outside testing
            run_command(['su', '-c', 'echo 1 >/sys/devices/virtual/graphics/fb0/cec'], shell=True)
        elif display_method == '8':  # Backlight on Raspberry Pi (kernel)
            # NOTE: Contrary to what you might think, 0 means on
            run_command(['su', '-c', 'echo 0 >/sys/class/backlight/rpi_backlight/bl_power'], shell=True)

    @atexit.register
    def __del__(self):
        del self._monitor
        self.close()


if __name__ == '__main__':
    addon = xbmcaddon.Addon()

    addon_name = addon.getAddonInfo('name')
    addon_id = addon.getAddonInfo('id')
    addon_path = addon.getAddonInfo('path').decode('utf-8')
    addon_icon = addon.getAddonInfo('icon')
    display_method = addon.getSetting('display_method')
    power_method = addon.getSetting('power_method')
    logoff = addon.getSetting('logoff')
    mute = addon.getSetting('mute')

    # Do not start screensaver when command fails
    screensaver = TurnOffScreensaver('gui.xml', addon_path, 'default')
    screensaver.doModal()
    del screensaver
