#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Code by madhouse
#Code Speedtest-cli from source https://github.com/sivel/speedtest-cli
from __future__ import print_function
import re
from Components.Button import Button
from os import remove, environ, chmod, path
import gettext
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve
from enigma import getDesktop, eConsoleAppContainer, ePicLoad
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.Label import Label
from skin import loadSkin
from Components.AVSwitch import AVSwitch

plugin_path = '/usr/lib/enigma2/python/Plugins/Extensions/InternetSpeedTest/speedtest.py'
font = resolveFilename(SCOPE_PLUGINS, "Extensions/InternetSpeedTest/fonts")
skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/InternetSpeedTest/")
cmd = 'python ' + plugin_path + ' --no-pre-allocate --share'
png_tmp = '/tmp/speedtest.png'

if path.exists(plugin_path):
    chmod(plugin_path, 0o755)
HD = getDesktop(0).size()
if HD.width() > 1280:
    loadSkin(skin_path + 'speedtest_fhd.xml')
else:
    loadSkin(skin_path + 'speedtest_hd.xml')

PluginLanguageDomain = "speedtest"
PluginLanguagePath = "Extensions/InternetSpeedTest/locale"

def localeInit():
    lang = language.getLanguage()[:2]
    environ["LANGUAGE"] = lang
    gettext.bindtextdomain(PluginLanguageDomain, PluginLanguagePath)
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))

def _(txt):
    if gettext.dgettext(PluginLanguageDomain, txt):
        return gettext.dgettext(PluginLanguageDomain, txt)
    else:
        return gettext.gettext(txt)
language.addCallback(localeInit())

from enigma import addFont
try:
    addFont("%s/Roboto-Regular.ttf" % font, "speedtest", 100, 1)
except Exception as ex:
    print(ex)

class internetspeedtest(Screen):
    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self.color = '#800080'
        self['data'] = Label(_('I check Internet speedtest, be patient...'))
        self['ping'] = Label('')
        self['host'] = Label('')
        self['ip'] = Label('')
        self['download'] = Label('')
        self['upload'] = Label('')
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Label()
        self['green'] = Pixmap()
        self['green'].hide()
        self['key_yellow'] = Label()
        self['yellow'] = Pixmap()
        self['yellow'].hide()
        self['key_blue'] = Label()
        self['blue'] = Pixmap()
        self['blue'].hide()
        self['image'] = Pixmap()
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {
            'cancel': self.exit,
            'red': self.exit,
            'blue': self.showresults,
            'green': self.testagain,
            'yellow': self.save_result}, -2)
        self.finished = False
        self.data = ''
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.action)
        self.container.dataAvail.append(self.dataAvail)
        self.container.execute(cmd)

    def showresults(self):
        self.session.open(showresult)

    def testagain(self):
        self['green'].hide()
        self['key_green'].setText('')
        self['yellow'].hide()
        self['key_yellow'].setText('')
        self['blue'].hide()
        self['key_blue'].setText('')
        self['ping'].setText('')
        self['host'].setText('')
        self['ip'].setText('')
        self['download'].setText('')
        self['upload'].setText('')
        if self.finished == False:
            return
        self.data = ''
        self.container.execute(cmd)

    def action(self, retval):
        print('retval',retval)
        print('finished test')
        self.finished = True

    def dataAvail(self, rstr):
        if rstr:
            rstr = str(rstr.decode())
            self.data = self.data + rstr
            parts = rstr.split('\n')
            for part in parts:
                if 'Hosted by' in part:
                    try:
                        host = part.split('Hosted by')[1].strip()
                    except:
                        host = ''
                    self['host'].setText(str(host))
                if 'Ping' in part:
                    try:
                        ping = rstr.split('Ping')[1].strip()
                    except:
                        ping = ''
                    self['ping'].setText(str(ping))
                if 'Testing download from' in part:
                    ip = part.split('Testing download from')[1].split(')')[0].replace('(','').strip()
                    self['ip'].setText(str(ip))
                    self.data = (_('Testing download from'))
                if 'Download:' in rstr:
                    try:
                        download = rstr.split(':')[1].split('\n')[0].strip()
                    except:
                        download = ''
                    self['download'].setText(str(download))
                    self.data = (_('Testing upload speed'))
                if 'Upload:' in rstr:
                    try:
                        upload = rstr.split(':')[1].split('\n')[0].strip()
                    except:
                        upload = ''
                    self['upload'].setText(str(upload))
                if 'Share results:' in rstr:
                    try:
                        url_results = rstr.split()[2]
                    except:
                        url_results = ''
                    self.url_png = str(url_results)
                    self['key_yellow'].setText(_('Save results'))
                    self['yellow'].show()
                    self['key_green'].setText(_('Repeat test'))
                    self['green'].show()
                    self['data'].setText(_('Test completed, to test again press green button'))
                    return
                self['data'].setText(_(self.data).replace('Hosted by', '').replace('.', ''))

    def save_result(self):
        try:
            urlretrieve(self.url_png, png_tmp)
        except Exception as e:
            print(e)
        if path.exists(png_tmp):
            self['data'].setText(_('Result successfully saved in /tmp/speedtest.png'))
            self['key_blue'].setText(_('Show results'))
            self['blue'].show()
        else:
            self['data'].setText(_('Download speedtest.png failed!'))

    def exit(self):
        self.container.appClosed.remove(self.action)
        self.container.dataAvail.remove(self.dataAvail)
        self.close()

class showresult(Screen):
    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self['key_red'] = Button(_('Exit'))
        self['image'] = Pixmap()
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {
            'cancel': self.close_screen,
            'red': self.close_screen}, -2)
        self.onLayoutFinish.append(self.showpng)

    def close_screen(self):
        self.close()

    def showpng(self):
        scale = AVSwitch().getFramebufferScale()
        width = 750
        height = 400
        if HD.width() > 1280:
            width = 1300
            height = 693
        self.picload = ePicLoad()
        if self.picload:
            self.picload.setPara([width, height, scale[0], scale[1], 0, 1, "FF000000"])
            self.picload.startDecode(png_tmp, 0, 0, False)
        png = self.picload.getData()
        if png is not None:
            self["image"].instance.setPixmap(png)

def main(session, **kwargs):
    session.open(internetspeedtest)

def Plugins(**kwargs):
    list = []
    if HD.width() > 1280:
        list.append(PluginDescriptor(name=('Internet Speed Test'), description=_('Test your internet speed'), where=[PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU], icon='speedtestfhd.png', fnc=main))
    else:
        list.append(PluginDescriptor(name=('Internet Speed Test'), description=_('Test your internet speed'), where=[PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU], icon='speedtest.png', fnc=main))
    return list
