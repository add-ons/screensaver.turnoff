# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals
import unittest
import time
import screensaver

xbmc = __import__('xbmc')
xbmcaddon = __import__('xbmcaddon')
xbmcgui = __import__('xbmcgui')


class TestScreensaver(unittest.TestCase):

    @staticmethod
    def test_screensaver_log():
        ''' Test screensaver logging '''
        screensaver.ADDON.settings['max_log_level'] = '0'
        screensaver.ADDON.settings['display_method'] = '0'
        screensaver.ADDON.settings['power_method'] = '0'
        turnoff = screensaver.TurnOffDialog('gui.xml', screensaver.ADDON_PATH, 'default')
        turnoff.onInit()
        time.sleep(2)
        turnoff.resume()

    @staticmethod
    def test_screensaver_builtin():
        ''' Test screensaver built-ins '''
        screensaver.ADDON.settings['display_method'] = '1'
        screensaver.ADDON.settings['power_method'] = '1'
        turnoff = screensaver.TurnOffDialog('gui.xml', screensaver.ADDON_PATH, 'default')
        turnoff.onInit()
        time.sleep(2)
        turnoff.resume()

    def test_screensaver_missing_command(self):
        ''' Test enabling screensaver '''
        screensaver.ADDON.settings['display_method'] = '2'
        screensaver.ADDON.settings['power_method'] = '2'
        turnoff = screensaver.TurnOffDialog('gui.xml', screensaver.ADDON_PATH, 'default')
        with self.assertRaises(SystemExit) as init:
            turnoff.onInit()  # No such file or directory
        self.assertEqual(init.exception.code, 2)
        time.sleep(2)
        with self.assertRaises(SystemExit) as resume:
            turnoff.resume()  # No such file or directory
        self.assertEqual(resume.exception.code, 2)

    @unittest.skip('This requires su privileges')
    def test_screensaver_failed_command(self):
        ''' Test screensaver failed command '''
        screensaver.ADDON.settings['display_method'] = '7'
        screensaver.ADDON.settings['power_method'] = '3'
        turnoff = screensaver.TurnOffDialog('gui.xml', screensaver.ADDON_PATH, 'default')
        with self.assertRaises(SystemExit) as init:
            turnoff.onInit()  # We cannot find the binary
        self.assertEqual(init.exception.code, 2)
        time.sleep(2)
        with self.assertRaises(SystemExit) as resume:
            turnoff.resume()  # We cannot find the binary
        self.assertEqual(resume.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
