# -*- coding: utf-8 -*-

import json
import os
import re

YEAR = 2018
CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
YEAR_DIRECTORY = os.path.join(CURRENT_DIRECTORY, str(YEAR))
SOURCE = os.path.join(YEAR_DIRECTORY, 'lineup.txt')
DEST = os.path.join(YEAR_DIRECTORY, 'lineup.json')

print 'Reading {SOURCE}...'.format(SOURCE=SOURCE)
with open(SOURCE, 'r') as f:
  LINES = f.readlines()

STAGE_RE = r'^[A-Z &’]+$'

print 'Processing...'

current_day = None
current_stage = None
current_day_stage = None
days = []
act_count = 0
for index, line in enumerate(LINES):
  line = line.strip()

  # Skip blank lines
  if not line:
    continue

  # Skip the header lines
  if line.endswith('\tTimes'):
    continue

  if line[-3:] == 'day':
    # This is the start of a new day
    current_day = {
      'day': line,
      'stages': [],
    }
    days.append(current_day)

  elif re.match(STAGE_RE, line):
    # This is the start of a new stage
    stage = line
    current_day_stage = {
      'stage': line,
      'acts': []
    }
    current_day['stages'].append(current_day_stage)

  elif '\t' in line:
    # This should be an artist/time line
    artist, time = line.split('\t')
    time = time.replace('–', '-')
    if '-' not in time:
      raise Exception('Expected time ("{}", line {}) to contain a dash (are they unicode dashes?)!'.format(time, index+1))
    time_from, time_to = time.split('-')

    current_day_stage['acts'].append({
      'artist': artist.strip(),
      'time_from': time_from.strip().replace('.', ':'),
      'time_to': time_to.strip().replace('.', ':'),
    })
    act_count += 1

  else:
    print 'Unknown line format (line {}): {}'.format(index+1, line)

print 'Writing {DEST}...'.format(DEST=DEST)

with open(DEST, 'w') as f:
  json.dump(days, f, sort_keys=True, indent=2)

print 'Done!'
print 'Found {day_count} days, {act_count} acts'.format(
  day_count=len(days),
  act_count=act_count,
)
