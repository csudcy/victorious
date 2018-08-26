import codecs
import json
import os

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

HOUR_MIN = 10
HOUR_MAX = 24

# Full table
HOUR_WIDTH = 50
MINUTE_WIDTH = float(HOUR_WIDTH) / 60.0
DAY_WIDTH = (HOUR_MAX - HOUR_MIN) * HOUR_WIDTH

# Compact table
HOUR_HEIGHT = 75
MINUTE_HEIGHT = float(HOUR_HEIGHT) / 60.0
DAY_HEIGHT = (HOUR_MAX - HOUR_MIN) * HOUR_HEIGHT

INCLUDED_STAGES = [
  'COMMON STAGE',
  'CASTLE STAGE',
]


###############################
# Utility functions
###############################

def hm_to_minutes(t):
  h, m = t.split(':')
  return int(h) * 60 + int(m)


def minutes_to_hm(hour, minute):
  return '{h:02}:{m:02}'.format(h=hour, m=minute)


def get_act_style(act, prefs):
  prefs = {
    person: score
    for person, person_prefs in prefs.items()
    for pref_act, score in person_prefs.items()
    if pref_act == act['artist']
  }
  if not prefs:
    return None

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


def get_time_div_compact(time_from, time_to, text, style=None):
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


def save(filename, content):
  print 'Writing {filename}...'.format(filename=filename)
  content = content.replace('><', '>\n<')
  with codecs.open(filename, 'w', 'utf-8') as f:
    f.write(content)


###############################
# Year based functions
###############################

def load_lineup(year):
  print 'Reading {year} lineup...'.format(year=year)
  filename = os.path.join(CURRENT_DIRECTORY, str(year), 'lineup.json')
  with open(filename, 'r') as f:
    return json.load(f)


def load_prefs(year):
  print 'Reading {year} prefs...'.format(year=year)
  filename = os.path.join(CURRENT_DIRECTORY, str(year), 'prefs.json')
  if not os.path.exists(filename):
    return {}
  with open(filename, 'r') as f:
    return json.load(f)


def output_full(year, prefs, lineup):
  print 'Processing (full)...'
  output = u'<html><head><title>Victorious {year}</title></head><body>'.format(year=year)
  output += '<a href="../">&lt;-- Index</a>&nbsp;&nbsp;&nbsp;&nbsp;'
  output += '<a href="lineup_compact.html">Compact Lineup</a>'

  for day in lineup:
    # Add the headers
    output += u'<h1>{day}</h1><table border="1"><thead><tr><td>Stage</td>'.format(day=day['day'])
    output += u'<td style="position: relative; height: 22px; min-width: {w}px;">'.format(w=DAY_WIDTH)
    for hour in xrange(HOUR_MIN, HOUR_MAX):
      time_from = minutes_to_hm(hour, 0)
      time_to = minutes_to_hm(hour + 1, 0)
      output += get_time_div(time_from, time_to, time_from)
    output += u'</td></tr></thead><tbody>'

    # Add the body
    for stage in day['stages']:
      output += u'<tr><td style="white-space: nowrap;">{stage}</td>'.format(stage=stage['stage'])
      output += u'<td style="position: relative; height: 22px;">'
      for act in stage['acts']:
        text = u'{artist} ({time_from} - {time_to})'.format(**act)
        style = get_act_style(act, prefs)
        output += get_time_div(act['time_from'], act['time_to'], text, style=style)
      output += u'</td>'
      output += u'</tr>'

    # Close up
    output += u'</tbody></table></body></html>'

  filename = os.path.join(CURRENT_DIRECTORY, str(year), 'lineup.html')
  save(filename, output)


def output_compact(year, prefs, lineup):
  print 'Processing (compact)...'
  output = u'<html><head><title>Victorious {year}</title></head><body>'.format(year=year)
  output += '<a href="../">&lt;-- Index</a>&nbsp;&nbsp;&nbsp;&nbsp;'
  output += '<a href="lineup.html">Full Lineup</a>'

  output += u'<table border="1" style="width: 100%;"><thead><tr><th>Time</th>'
  for stage in INCLUDED_STAGES:
    output += u'<th>{stage}</th>'.format(stage=stage)
  output += u'</tr></thead><tbody>'


  for day in lineup:
    # Add the headers
    output += u'<tr><td colspan="{cols}" style="font-size: 2em; font-weight: bold; text-align:center;">{day}</td></tr>'.format(
      cols=len(INCLUDED_STAGES)+1, day=day['day'])

    # Add the time column
    output += u'<td style="position: relative; height: {height}px;">'.format(height=DAY_HEIGHT)
    for hour in xrange(HOUR_MIN, HOUR_MAX):
      time_from = minutes_to_hm(hour, 0)
      time_to = minutes_to_hm(hour + 1, 0)
      output += get_time_div_compact(time_from, time_to, time_from)
    output += u'</td>'

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
        output += '<td>&nbsp;</td>'
        continue

      stage = stages[0]

      # Add the stage column
      output += u'<td style="position: relative; height: {height}px;">'.format(height=DAY_HEIGHT)
      for act in stage['acts']:
        text = u'{artist}<br/>{time_from} - {time_to}'.format(**act)
        style = get_act_style(act, prefs)
        output += get_time_div_compact(act['time_from'], act['time_to'], text, style=style)
      output += u'</td>'

    output += u'</tr>'

  # Close up
  output += u'</tbody></table></body></html>'

  filename = os.path.join(CURRENT_DIRECTORY, str(year), 'lineup_compact.html')
  save(filename, output)


def process_year(year):
  lineup = load_lineup(year)
  prefs = load_prefs(year)
  output_full(year, prefs, lineup)
  output_compact(year, prefs, lineup)


if __name__ == '__main__':
  process_year(2017)
  process_year(2018)
