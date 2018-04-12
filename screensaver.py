import sys
import subprocess

import xbmc
import xbmcaddon
import xbmcgui


def _popup(title='', msg='', delay=5000, image= ''):
    xbmc.executebuiltin('XBMC.Notification("%s","%s",%d,"%s")' % (title, msg, delay, image))

def _run_builtin(builtin):
    xbmc.log(msg="[%s] Executing builtin '%s'" % (addon_name, builtin), level=xbmc.LOGNOTICE)
    try:
        xbmc.executebuiltin(builtin)
    except Exception as e:
        xbmc.log(msg="[%s] Exception executing builtin '%s': %s" % (addon_name, builtin, e), level=xbmc.LOGERROR)
        _popup(title='Screensaver failed', msg="[%s] Exception executing builtin '%s': %s" % (addon_name, builtin, e))

def _run_command(command, shell=False):
    # TODO: Add options for running using su or sudo
    try:
        cmd = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell)
        (out, err) = cmd.communicate()
        if cmd.returncode == 0:
            xbmc.log(msg="[%s] Running command '%s' returned rc=%s" % (addon_name, ' '.join(command), cmd.returncode), level=xbmc.LOGNOTICE)
        else:
            xbmc.log(msg="[%s] Running command '%s' failed with rc=%s" % (addon_name, ' '.join(command), cmd.returncode), level=xbmc.LOGERROR)
            if err:
                xbmc.log(msg="[%s] Command '%s' returned on stderr: %s" % (addon_name, command[0], err), level=xbmc.LOGERROR)
            if out:
                xbmc.log(msg="[%s] Command '%s' returned on stdout: %s " % (addon_name, command[0], out), level=xbmc.LOGERROR)
            _popup(title='Screensaver failed', msg="%s\n%s" % (out, err))
            sys.exit(1)
    except Exception as e:
        xbmc.log(msg="[%s] Exception running '%s': %s" % (addon_name, command[0], e), level=xbmc.LOGERROR)
        _popup(title='Screensaver failed', msg="Exception running '%s': %s" % (command[0], e))
        sys.exit(2)
    # TODO: Show pop-up on failure


class Screensaver(xbmcgui.WindowXMLDialog):

    class Monitor(xbmc.Monitor):

        def __init__(self, callback):
            self._callback = callback

        def onScreensaverDeactivated(self):
            self._callback()

    def onInit(self):
        self._monitor = self.Monitor(self.exit)

        # Power off system
        xbmc.log(msg='[%s] Turn system off using method %s' % (addon_name, power_method), level=xbmc.LOGNOTICE)
        if power_method == '1':  # Suspend (built-in)
            _run_builtin('Suspend')
        elif power_method == '2':  # ShutDown action (built-in)
            _run_builtin('Hibernate')
        elif power_method == '3':  # ShutDown action (built-in)
            _run_builtin('Quit')
        elif power_method == '4':  # ShutDown action (built-in)
            _run_builtin('ShutDown')
        elif power_method == '5':  # Reboot (built-in)
            _run_builtin('Reboot')
        elif power_method == '6':  # PowerDown (built-in)
            _run_builtin('PowerDown')
        elif power_method == '7':  # Android POWER key event (using input)
            _run_command(['su', '-c', 'input keyevent KEYCODE_POWER'], shell=True)

    def onAction(self, action):
        self.exit()

    def exit(self):
        # Unmute audio
        if mute == 'true':
            _run_builtin('Mute')

        # Turn on display
        xbmc.log(msg='[%s] Turn display signal back on using method %s' % (addon_name, display_method), level=xbmc.LOGNOTICE)
        if display_method == '1':  # CEC Standby (built-in)
            _run_builtin('CECActivateSource')
        elif display_method == '2':  # Raspberry Pi (using vcgencmd)
            _run_command(['vcgencmd', 'display_power', '1'])
        elif display_method == '3':  # DPMS (built-in)
            _run_builtin('ToggleDPMS')
        elif display_method == '4':  # X11 DPMS (using xset)
            _run_command(['xset', 'dpms', 'force', 'on'])
        elif display_method == '5':  # DPMS (using vbetool)
            _run_command(['vbetool', 'dpms', 'on'])
        elif display_method == '6':  # DPMS (using xrandr)
            # NOTE: This needs more outside testing
            _run_command(['xrandr', '--output CRT-0', 'on'])
        elif display_method == '7':  # Android CEC (kernel)
            # NOTE: This needs more outside testing
            _run_command(['su', '-c', 'echo 1 >/sys/devices/virtual/graphics/fb0/cec'], shell=True)

        del self._monitor
        self.close()

if __name__ == '__main__':
    addon = xbmcaddon.Addon()

    addon_name = addon.getAddonInfo('name')
    addon_path = addon.getAddonInfo('path')
    display_method = addon.getSetting('display_method')
    power_method = addon.getSetting('power_method')
    logoff = addon.getSetting('logoff')
    mute = addon.getSetting('mute')

    # Turn off display
    xbmc.log(msg='[%s] Turn display signal off using method %s' % (addon_name, display_method), level=xbmc.LOGNOTICE)
    if display_method == '1':  # CEC Standby (built-in)
        _run_builtin('CECStandby')
    elif display_method == '2':  # Raspberry Pi (using vcgencmd)
        _run_command(['vcgencmd', 'display_power', '0'])
    elif display_method == '3':  # DPMS (built-in)
        _run_builtin('ToggleDPMS')
    elif display_method == '4':  # X11 DPMS (using xset)
        _run_command(['xset', 'dpms', 'force', 'off'])
    elif display_method == '5':  # DPMS (using vbetool)
        _run_command(['vbetool', 'dpms', 'off'])
    elif display_method == '6':  # DPMS (using xrandr)
        # NOTE: This needs more outside testing
        _run_command(['xrandr', '--output CRT-0', 'off'])
    elif display_method == '7':  # Android CEC (kernel)
        # NOTE: This needs more outside testing
        _run_command(['su', '-c', 'echo 0 >/sys/devices/virtual/graphics/fb0/cec'], shell=True)


    # FIXME: Screensaver always seems to log off when logged in ?
    # Log off user
    if logoff == 'true':
        _run_builtin('System.Logoff()')

    # Mute audio
    if mute == 'true':
        _run_builtin('Mute')

    # Do not start screensaver when command fails
    screensaver = Screensaver('screensaver-nosignal.xml', addon_path, 'default')
    screensaver.doModal()
    del screensaver
