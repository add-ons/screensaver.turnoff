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

addon = xbmcaddon.Addon()


class TestScreensaver(unittest.TestCase):

    @staticmethod
    def test_screensaver_log():
        ''' Test screensaver logging '''
        addon.settings['max_log_level'] = '0'
        addon.settings['display_method'] = '0'
        addon.settings['power_method'] = '0'
        turnoff = screensaver.TurnOffDialog('gui.xml', screensaver.addon_path(), 'default')
        turnoff.onInit()
        time.sleep(2)
        turnoff.resume()

    @staticmethod
    def test_screensaver_builtin():
        ''' Test screensaver built-ins '''
        addon.settings['display_method'] = '1'
        addon.settings['power_method'] = '1'
        turnoff = screensaver.TurnOffDialog('gui.xml', screensaver.addon_path(), 'default')
        turnoff.onInit()
        time.sleep(2)
        turnoff.resume()

    def test_screensaver_missing_command(self):
        ''' Test enabling screensaver '''
        addon.settings['display_method'] = '2'
        addon.settings['power_method'] = '2'
        turnoff = screensaver.TurnOffDialog('gui.xml', screensaver.addon_path(), 'default')
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
        addon.settings['display_method'] = '7'
        addon.settings['power_method'] = '3'
        turnoff = screensaver.TurnOffDialog('gui.xml', screensaver.addon_path(), 'default')
        with self.assertRaises(SystemExit) as init:
            turnoff.onInit()  # We cannot find the binary
        self.assertEqual(init.exception.code, 2)
        time.sleep(2)
        with self.assertRaises(SystemExit) as resume:
            turnoff.resume()  # We cannot find the binary
        self.assertEqual(resume.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
