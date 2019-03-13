import atexit
import subprocess
import sys

import xbmc
import xbmcaddon
import xbmcgui

# NOTE: The below order relates to resources/settings.xml
DISPLAY_METHODS = [
    dict(name='do-nothing', title='Do nothing',
         function='log_info', args_off='Do nothing to power off display', args_on='Do nothing to power back on display'),
    dict(name='cec-builtin', title='CEC (buil-in)',
         function='run_builtin', args_off='CECStandby', args_on='CECActivateSource'),
    dict(name='no-signal-rpi', title='No Signal on Raspberry Pi (using vcgencmd)',
         function='run_command',
         args_off=['vcgencmd', 'display_power', '0'],
         args_on=['vcgencmd', 'display_power', '1']),
    dict(name='dpms-builtin', title='DPMS (built-in)',
         function='run_builtin', args_off='ToggleDPMS', args_on='ToggleDPMS'),
    dict(name='dpms-xset', title='DPMS (using xset)',
         function='run_command',
         args_off=['xset', 'dpms', 'force', 'off'],
         args_on=['xset', 'dpms', 'force', 'on']),
    dict(name='dpms-vbetool', title='DPMS (using vbetool)',
         function='run_command',
         args_off=['vbetool', 'dpms', 'off'],
         args_on=['vbetool', 'dpms', 'on']),
    # TODO: This needs more outside testing
    dict(name='dpms-xrandr', title='DPMS (using xrandr)',
         function='run_command',
         args_off=['xrandr', '--output CRT-0', 'off'],
         args_on=['xrandr', '--output CRT-0', 'on']),
    # TODO: This needs more outside testing
    dict(name='cec-android', title='CEC on Android (kernel)',
         function='run_command',
         args_off=['su', '-c', 'echo 0 >/sys/devices/virtual/graphics/fb0/cec'],
         args_on=['su', '-c', 'echo 1 >/sys/devices/virtual/graphics/fb0/cec']),
    # NOTE: Contrary to what one might think, 1 means off and 0 means on
    dict(name='backlight-rpi', title='Backlight on Raspberry Pi (kernel)',
         function='run_command',
         args_off=['su', '-c', 'echo 1 >/sys/class/backlight/rpi_backlight/bl_power'],
         args_on=['su', '-c', 'echo 0 >/sys/class/backlight/rpi_backlight/bl_power']),
]

POWER_METHODS = [
    dict(name='do-nothing', title='Do nothing',
         function='log_info', args_off='Do nothing to power off system'),
    dict(name='suspend-builtin', title='Suspend (built-in)',
         function='run_builtin', args_off='Suspend'),
    dict(name='hibernate-builtin', title='Hibernate (built-in)',
         function='run_builtin', args_off='Hibernate'),
    dict(name='quit-builtin', title='Quit (built-in)',
         function='run_builtin', args_off='Quit'),
    dict(name='shutdown-builtin', title='ShutDown action (built-in)',
         function='run_builtin', args_off='ShutDown'),
    dict(name='reboot-builtin', title='Reboot (built-in)',
         function='run_builtin', args_off='Reboot'),
    dict(name='powerdown-builtin', title='Powerdown (built-in)',
         function='run_builtin', args_off='Powerdown'),
]


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


def func(function, *args):
    return globals()[function](*args)


class TurnOffMonitor(xbmc.Monitor):

    def __init__(self, *args, **kwargs):
        self.action = kwargs['action']

    def onScreensaverDeactivated(self):
        self.action()


class TurnOffScreensaver(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        self.monitor = None

    def onInit(self):
        self.display_method = int(addon.getSetting('display_method'))
        self.display = DISPLAY_METHODS[self.display_method]
        self.power_method = int(addon.getSetting('power_method'))
        self.power = POWER_METHODS[self.power_method]
        self.logoff = addon.getSetting('logoff')
        self.mute = addon.getSetting('mute')

        log_notice(msg='display_method=%s, power_method=%s, logoff=%s, mute=%s' % (self.display['name'], self.power['name'], self.logoff, self.mute))

        self.monitor = TurnOffMonitor(action=self.resume)

        # Mute audio
        if self.mute == 'true':
            log_notice(msg='Mute audio')
            set_mute(True)
            # NOTE: Since the Mute-builtin is a toggle, we need to do this to ensure Mute
#            run_builtin('VolumeDown')
#            run_builtin('Mute')

        # FIXME: Screensaver always seems to lock when started, requires unlock and re-login
        # Log off user
        if self.logoff == 'true':
            log_notice(msg='Log off user')
            run_builtin('ActivateWindow("LoginScreen")')
#            run_builtin('System.LogOff')

        # Turn off display
        if self.display_method != 0:
            log_notice(msg="Turn display signal off using method '%s'" % self.display['name'])
        func(self.display['function'], self.display['args_off'])

        # Power off system
        if self.power_method != 0:
            log_notice(msg="Turn system off using method '%s'" % self.power['name'])
        func(self.power['function'], self.power['args_off'])

    def resume(self):
        # Turn on display
        if self.display_method != 0:
            log_notice(msg="Turn display signal back on using method '%s'" % self.display['name'])
        func(self.display['function'], self.display['args_on'])

        # Unmute audio
        if self.mute == 'true':
            log_notice(msg='Unmute audio')
            set_mute(False)
#            run_builtin('Mute')
            # NOTE: Since the Mute-builtin is a toggle, we need to do this to ensure Unmute
#            run_builtin('VolumeUp')

    @atexit.register
    def __del__(self):
        del self.monitor
        self.close()


if __name__ == '__main__':
    addon = xbmcaddon.Addon()

    addon_name = addon.getAddonInfo('name')
    addon_id = addon.getAddonInfo('id')
    addon_path = addon.getAddonInfo('path').decode('utf-8')
    addon_icon = addon.getAddonInfo('icon')

    # Do not start screensaver when command fails
    screensaver = TurnOffScreensaver('gui.xml', addon_path, 'default')
    screensaver.doModal()
    del screensaver
