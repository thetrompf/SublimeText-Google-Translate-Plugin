# -*- coding: utf-8 -*-
# author:mtimer
# author:thetrompf
# https://github.com/MtimerCMS/SublimeText-Google-Translate-Plugin (forked from)
# https://github.com/thetrompf/SublimeText-Google-Translate-Plugin

import sublime
import sublime_plugin
try:
  from urllib import urlopen, urlencode
except:
  from urllib.request import urlopen
  from urllib.parse import urlencode
from urllib.request import Request
import json
import re

settings = sublime.load_settings("goTranslate.sublime-settings")
api_url = 'http://translate.google.com.hk/translate_a/t?client=t&hl=en&ie=UTF-8&oe=UTF-8&multires=1&otf=2&ssel=0&tsel=0&sc=1&%s'
last_source_language = settings.get('source_language') if settings.has('source_language') else ''
last_target_language = settings.get('target_language') if settings.has('target_language') else ''

class GoTranslateCommand(sublime_plugin.TextCommand):

  def run(self, edit, **args):
    source_language = args['source_language'] if 'source_language' in args else settings.get("source_language")
    target_language = args['target_language'] if 'target_language' in args else settings.get("target_language")

    for region in self.view.sel():
      if not region.empty():
        selection = self.view.substr(region)

        result = translate(selection, source_language, target_language)

        text = (json.dumps(result[0][0][0], ensure_ascii = False)).strip('"').replace('\\n', "\n").replace('\\t', "\t").replace('\\"', '"')

        # print (text)
        self.view.replace(edit, region, text)

  def is_visible(self):
    for region in self.view.sel():
      if not region.empty():
        return True
    return False

class GoTranslateWithTargetLanguageFromInputCommand(sublime_plugin.WindowCommand):

  def run(self):
    global last_source_language
    self.window.show_input_panel('Source langauge', last_source_language,
      self.on_source_done, self.on_source_change, self.on_source_cancel)

  def on_source_done(self, input):
    global last_source_language, last_target_language
    last_source_language = input
    self.window.show_input_panel('Target langauge', last_target_language,
      self.on_target_done, self.on_target_change, self.on_target_cancel)

  def on_target_done(self,input):
    global last_source_language, last_target_language
    last_target_language = input
    self.window.active_view().run_command('go_translate', {"source_language": last_source_language, "target_language": last_target_language})

  def on_source_change(self, input):
    pass

  def on_source_cancel(self):
    pass

  def on_target_change(self, input):
    pass

  def on_target_cancel(self):
    pass

def translate(text, sl, tl):
  if sl:
    data = urlencode({'text': text, 'sl': sl, 'tl': tl})
  else:
    data = urlencode({'text': text, 'sl': 'auto', 'tl': tl})

  request = Request(api_url % data)
  request.add_header('User-Agent', 'Mozilla/5.0')
  if sublime.version() < '3':
    result = urlopen(request).read()
    fixed_json = re.sub(r',{2,}', ',', result).replace(',]', ']')
    jsons = json.loads(fixed_json.decode("utf-8"))
  else:
    result = urlopen(request).read().decode("utf-8")
    fixed_json = re.sub(r',{2,}', ',', result).replace(',]', ']')
    jsons = json.loads(fixed_json)
  return jsons


def plugin_loaded():
  global settings
  settings = sublime.load_settings("goTranslate.sublime-settings")
