import codecs
import json
import os

YEAR = 2018
CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
YEAR_DIRECTORY = os.path.join(CURRENT_DIRECTORY, str(YEAR))
SOURCE = os.path.join(YEAR_DIRECTORY, 'lineup.json')
DEST_FULL = os.path.join(YEAR_DIRECTORY, 'lineup.html')
DEST_SMALL = os.path.join(YEAR_DIRECTORY, 'lineup_small.html')
PREFS_SOURCE = os.path.join(YEAR_DIRECTORY, 'prefs.json')

HOUR_MIN = 10
HOUR_MAX = 24

# Full table
HOUR_WIDTH = 50
MINUTE_WIDTH = float(HOUR_WIDTH) / 60.0
DAY_WIDTH = (HOUR_MAX - HOUR_MIN) * HOUR_WIDTH

# Small table
HOUR_HEIGHT = 75
MINUTE_HEIGHT = float(HOUR_HEIGHT) / 60.0
DAY_HEIGHT = (HOUR_MAX - HOUR_MIN) * HOUR_HEIGHT

INCLUDED_STAGES = [
  'COMMON STAGE',
  'CASTLE STAGE',
]

print 'Reading {SOURCE}...'.format(SOURCE=SOURCE)
with open(SOURCE, 'r') as f:
  DAYS = json.load(f)

if os.path.exists(PREFS_SOURCE):
  with open(PREFS_SOURCE, 'r') as f:
    PREFS = json.load(f)
else:
  PREFS = {}

def hm_to_minutes(t):
  h, m = t.split(':')
  return int(h) * 60 + int(m)

def minutes_to_hm(hour, minute):
  return '{h:02}:{m:02}'.format(h=hour, m=minute)

def get_act_style(act):
  prefs = {
    person: score
    for person, person_prefs in PREFS.items()
    for pref_act, score in person_prefs.items()
    if pref_act == act['artist']
  }
  if not prefs:
    return None

  text += ' (' + ', '.join(prefs.keys()) + ')'
  max_score = max(prefs.values())
  return 'background-color: rgba(255, 0, 255, {a});'.format(a=float(max_score)/5.0)

def get_time_div(time_from, time_to, text, style=None):
  minutes_from = hm_to_minutes(time_from)
  minutes_to = hm_to_minutes(time_to)
  left = (minutes_from - (HOUR_MIN * 60)) * MINUTE_WIDTH
  width = (minutes_to - minutes_from) * MINUTE_WIDTH - 2
  style = style or ''
  return u'<div style="position: absolute; top: 0px; left: {l}px; width: {w}px; height: 20px; border: 1px solid black; overflow: hidden; {style}" title="{text}">{text}</div>'.format(
    l=left,
    w=width,
    text=text,
    style=style,
  )

def get_time_div_small(time_from, time_to, text, style=None):
  minutes_from = hm_to_minutes(time_from)
  minutes_to = hm_to_minutes(time_to)
  top = (minutes_from - (HOUR_MIN * 60)) * MINUTE_HEIGHT
  height = (minutes_to - minutes_from) * MINUTE_HEIGHT - 2
  style = style or ''
  return u'<div style="position: absolute; top: {t}px; height: {h}px; left: 0px; right: 0px; border: 1px solid black; overflow: hidden; white-space: nowrap; {style}" title="{title}">{text}</div>'.format(
    t=top,
    h=height,
    title=text.replace('<br/>', '\n'),
    text=text,
    style=style,
  )

def output_full():
  print 'Processing (full)...'
  OUTPUT = u'<html><head><title>Victorious {YEAR}</title></head><body>'.format(YEAR=YEAR)

  for day in DAYS:
    # Add the headers
    OUTPUT += u'<h1>{day}</h1><table border="1"><thead><tr><td>Stage</td>'.format(day=day['day'])
    OUTPUT += u'<td style="position: relative; height: 22px; min-width: {w}px;">'.format(w=DAY_WIDTH)
    for hour in xrange(HOUR_MIN, HOUR_MAX):
      time_from = minutes_to_hm(hour, 0)
      time_to = minutes_to_hm(hour + 1, 0)
      OUTPUT += get_time_div(time_from, time_to, time_from)
    OUTPUT += u'</td></tr></thead><tbody>'

    # Add the body
    for stage in day['stages']:
      OUTPUT += u'<tr><td style="white-space: nowrap;">{stage}</td>'.format(stage=stage['stage'])
      OUTPUT += u'<td style="position: relative; height: 22px;">'
      for act in stage['acts']:
        text = u'{artist} ({time_from} - {time_to})'.format(**act)
        style = get_act_style(act)
        OUTPUT += get_time_div(act['time_from'], act['time_to'], text, style=style)
      OUTPUT += u'</td>'
      OUTPUT += u'</tr>'

    # Close up
    OUTPUT += u'</tbody></table></body></html>'

  print 'Writing {DEST_FULL}...'.format(DEST_FULL=DEST_FULL)

  with codecs.open(DEST_FULL, 'w', 'utf-8') as f:
    f.write(OUTPUT)

def output_small():
  print 'Processing (small)...'
  OUTPUT = u'<html><head><title>Victorious {YEAR}</title></head><body>'.format(YEAR=YEAR)

  OUTPUT += u'<table border="1" style="width: 100%;"><thead><tr><th>Time</th>'
  for stage in INCLUDED_STAGES:
    OUTPUT += u'<th>{stage}</th>'.format(stage=stage)
  OUTPUT += u'</tr></thead><tbody>'


  for day in DAYS:
    # Add the headers
    OUTPUT += u'<tr><td colspan="{cols}" style="font-size: 2em; font-weight: bold; text-align:center;">{day}</td></tr>'.format(
      cols=len(INCLUDED_STAGES)+1, day=day['day'])

    # Add the time column
    OUTPUT += u'<td style="position: relative; height: {height}px;">'.format(height=DAY_HEIGHT)
    for hour in xrange(HOUR_MIN, HOUR_MAX):
      time_from = minutes_to_hm(hour, 0)
      time_to = minutes_to_hm(hour + 1, 0)
      OUTPUT += get_time_div_small(time_from, time_to, time_from)
    OUTPUT += u'</td>'

    # Add each stage column
    for stage_name in INCLUDED_STAGES:
      # Find the stage for today
      stages = [
        stage
        for stage in day['stages']
        if stage['stage'] == stage_name
      ]

      # Check it is on today
      if not stages:
        OUTPUT += '<td>&nbsp;</td>'
        continue

      stage = stages[0]

      # Add the stage column
      OUTPUT += u'<td style="position: relative; height: {height}px;">'.format(height=DAY_HEIGHT)
      for act in stage['acts']:
        text = u'{artist}<br/>{time_from} - {time_to}'.format(**act)
        style = get_act_style(act)
        OUTPUT += get_time_div_small(act['time_from'], act['time_to'], text, style=style)
      OUTPUT += u'</td>'

    OUTPUT += u'</tr>'

  # Close up
  OUTPUT += u'</tbody></table></body></html>'

  print 'Writing {DEST_SMALL}...'.format(DEST_SMALL=DEST_SMALL)

  with codecs.open(DEST_SMALL, 'w', 'utf-8') as f:
    f.write(OUTPUT)

output_full()
output_small()
