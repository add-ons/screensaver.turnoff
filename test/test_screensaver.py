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
    turnoff = screensaver.TurnOffDialog('gui.xml', screensaver.ADDON_PATH, 'default')

    def test_screensaver(self):
        ''' Test enabling screensaver '''
        self.turnoff.onInit()
        time.sleep(5)
        self.turnoff.resume()


if __name__ == '__main__':
    unittest.main()
