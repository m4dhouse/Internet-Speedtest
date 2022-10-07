# -*- coding: utf-8 -*-
#Code by madhouse
#Code Speedtest-cli from source https://github.com/sivel/speedtest-cli
from os import remove, environ, chmod, path
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from skin import loadSkin
import gettext
from Components.Language import language
from enigma import addFont, getDesktop

plugin_path = "/usr/lib/enigma2/python/Plugins/Extensions/InternetSpeedTest/speedtest.py"
font = resolveFilename(SCOPE_PLUGINS, "Extensions/InternetSpeedTest/fonts")
skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/InternetSpeedTest/")
cmd = "python " + plugin_path + " --no-pre-allocate --share --secure"
png_tmp = "/tmp/speedtest.png"
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
	   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
	   "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
	   "Accept-Encoding": "none",
	   "Accept-Language": "en-US,en;q=0.8",
	   "Connection": "keep-alive"}

if path.exists(plugin_path):
	chmod(plugin_path, 0o755)
HD = getDesktop(0).size()
if HD.width() > 1280:
	loadSkin(skin_path + "speedtest_fhd.xml")
else:
	loadSkin(skin_path + "speedtest_hd.xml")

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

localeInit()
language.addCallback(localeInit)

try:
	addFont("%s/RegularFull.ttf" % font, "speedtest", 100, 1)
except Exception as ex:
	print(ex)
