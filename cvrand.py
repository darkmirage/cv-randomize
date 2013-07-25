#! /usr/bin/env python
import sys
import os.path
import random
import json
from copy import deepcopy
from docx import *


def rInt(a, b):
  return random.randint(a, b)


def writeDocx(doc, filename):
  coreprops = coreproperties(title='CV', subject='', creator='',
                             keywords=[])

  savedocx(doc, coreprops, appproperties(), contenttypes(), websettings(),
           wordrelationships(relationshiplist()), filename)


def loadTemplate(tmpl_path):
  try:
    template = opendocx(os.path.join(tmpl_path))
  except:
    print "Error loading template file."
    exit()
  return template


def findTargets(doc):
  text = '\n'.join(getdocumenttext(doc))
  tag_re = re.compile(r'\[(.+)\]')
  targets = tag_re.findall(text)
  targets.sort()
  return targets


def getFunction(functions, t):
  _t = t.split('.')
  return functions[_t[0]]

if __name__ == '__main__':

  tmpl_path = sys.argv[1]
  if (len(sys.argv) > 2):
    n = int(sys.argv[2])
  else:
    n = 5

  dir_path = os.path.dirname(os.path.realpath(__file__))
  data_path = os.path.join(dir_path, 'data')
  template = loadTemplate(tmpl_path)
  targets = findTargets(template)

  try:
    f = open(os.path.join(data_path, 'functions.json'), 'r')
    functions = json.loads(f.read())
    for t in functions:
      functions[t] = lambda s=functions[t]: eval(s)
  except:
    pass

  for t in targets:
    _t = t.split('.')
    if _t[0] in functions:
      continue
    try:
      f = open(os.path.join(data_path, _t[0] + '.json'), 'r')
      functions[_t[0]] = lambda l=json.loads(f.read()): l
    except:
      pass

  print "Generating CVs."

  memo = dict()
  list_re = re.compile(r'^_(.+)_$')
  for i in xrange(0, n):
    doc = deepcopy(template)
    dependence = {}
    for t in targets:
      value = 'NOT FOUND'

      _t = t.split('.')
      if _t[0] not in functions:
        continue

      value = functions[_t[0]]()
      if type(value) is list:
        if _t[0] in dependence:
          r = dependence[_t[0]]
        else:
          r = rInt(0, len(value)-1)
          dependence[_t[0]] = r

        if len(_t) > 1:
          value = value[r][_t[1]]
        else:
          value = value[r]

        if type(value) is list:
          value = value[rInt(0, len(value)-1)]

        m = list_re.match(value)
        if m:
          if m.group(0) not in memo:
            try:
              path = os.path.join(data_path, '%s.%s.json' % (_t[0], m.group(1)))
              f = open(path, 'r')
              memo[m.group(0)] = json.loads(f.read())
            except:
              value = "ERROR"
              print "Error reading in %s" % s
              continue

          l = memo[m.group(0)]
          value = l[rInt(0, len(l)-1)]

      doc = advReplace(doc, ur'(\[' + t + r'\])', value, 5)

    filename = os.path.join('output', 'cv_%04d.docx' % i)
    print filename
    writeDocx(doc, filename)

  print "Done."
