import subprocess

import xbmc
import xbmcaddon
import xbmcgui

class Screensaver(xbmcgui.WindowXMLDialog):

    class Monitor(xbmc.Monitor):

        def __init__(self, callback):
            self._callback = callback

        def onScreensaverDeactivated(self):
            self._callback()

    def onInit(self):
        self._monitor = self.Monitor(self.exit)

        # FIXME: Screensaver always seems to log off ?
        # Log off user
        if method == '0' or logoff == 'false':
            xbmc.log(msg='%s: Do not log off user' % addon_name, level=xbmc.LOGNOTICE)
        else:
            xbmc.log(msg='%s: Log off user' % addon_name, level=xbmc.LOGNOTICE)
            xbmc.executebuiltin('System.Logoff()')

        # Turn off display power
        xbmc.log(msg='%s: Turn display signal off using method %s' % (addon_name, method), level=xbmc.LOGNOTICE)
        if method == '1':
            subprocess.call(['vcgencmd', 'display_power', '0'])
        elif method == '2':
            subprocess.call(['xset', 'dpms', 'force', 'off'])
        elif method == '3':
            try:
                xbmc.executebuiltin('ToggleDPMS')
            except Exception as e:
                xbmc.log(msg="%s Failed to toggle DPMS: %s" % (addon_name, e), level=xbmc.LOGERROR)
        elif method == '4':
            try:
                xbmc.executebuiltin('CECStandby')
            except Exception as e:
                xbmc.log(msg="%s Failed to turn device off via CEC: %s" % (addon_name, e), level=xbmc.LOGERROR)


    def onAction(self):
        self.exit()

    def exit(self):
        # Turn on display power
        xbmc.log(msg='%s: Turn display signal back on using method %s' % (addon_name, method), level=xbmc.LOGNOTICE)
        if method == '1':
            subprocess.call(['vcgencmd', 'display_power', '1'])
        elif method == '2':
            subprocess.call(['xset', 'dpms', 'force', 'on'])
        elif method == '3':
            try:
                xbmc.executebuiltin('ToggleDPMS')
            except Exception as e:
                xbmc.log(msg="%s Failed to toggle DPMS: %s" % (addon_name, e), level=xbmc.LOGERROR)
        elif method == '4':
            try:
                xbmc.executebuiltin('CECActivateSource')
            except Exception as e:
                xbmc.log(msg="%s Failed to turn device off via CEC: %s" % (addon_name, e), level=xbmc.LOGERROR)

        self.close()

if __name__ == '__main__':
    addon = xbmcaddon.Addon()

    addon_name = addon.getAddonInfo('name')
    addon_path = addon.getAddonInfo('path')
    logoff = addon.getSetting('logoff')
    method = addon.getSetting('method')

    screensaver = Screensaver('screensaver-nosignal.xml', addon_path, 'default')
    screensaver.doModal()
    del screensaver
