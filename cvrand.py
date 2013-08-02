#! /usr/bin/env python
import sys
import os.path
import random
import json
import string
from copy import deepcopy
from docx import *


def rInt(a, b):
  return random.randint(a, b)


_tag_re = re.compile(r'\[([^\]]+)\]')


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
  targets = _tag_re.findall(text)
  targets.sort()
  return targets

def sanitizeFilename(filename):
  valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
  return ''.join(c for c in filename if c in valid_chars)


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
  tmpl_name = os.path.split(tmpl_path)[1]
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
      # Lazy reading
      functions[_t[0]] = lambda l=json.loads(f.read()): l
    except:
      pass

  print "Generating CVs."

  # Tracks external files not defined in functions
  memo = dict()

  list_re = re.compile(r'^_(.+)_$')
  for i in xrange(0, n):
    doc = deepcopy(template)

    # Ensures that linked variables are selected together
    dependence = {}

    # Results
    results = {}

    for t in targets:
      value = 'NOT FOUND'

      _t = t.split('.')
      if _t[0] not in functions:
        continue

      # Evaluate the function to get either a random result or a list to pick from
      value = functions[_t[0]]()
      if type(value) is list:
        if _t[0] in dependence:
          r = dependence[_t[0]]
        else:
          r = rInt(0, len(value)-1)
          dependence[_t[0]] = r

        # If the field is a subfield, retrieve the subfield
        if len(_t) > 1:
          value = value[r][_t[1]]
        else:
          value = value[r]

        # If the value is a list, or if it refers to an external file, randomize again
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

      doc = advReplace(doc, r'(\[' + t + r'\])', value, 5)
      results[t] = value

    filename = '%04d_%s' % (i, tmpl_name)
    tags = _tag_re.findall(filename)
    for t in tags:
      if t in results:
        filename = re.sub(r'(\[' + t + r'\])', str(results[t]), filename)
    filename = os.path.join('output', sanitizeFilename(filename))
    writeDocx(doc, filename)
    print filename

  print "Done."
