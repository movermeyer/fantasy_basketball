#  Copyright (C) 2014 Devin Kelly
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Devin Kelly"

import pycurl
import time
import sys
import os
import errno

from Util import mkdir_p

base_draft_url = "http://www.basketball-reference.com/draft/NBA_{year}.html"
base_team_url = "http://www.basketball-reference.com/teams/{team}/{year}.html"
default_dir = os.path.expanduser("~/.fantasy_basketball")


def download_data(data_dir, teams, drafts, league, year, league_id):
   data_dir = os.path.join(data_dir, 'raw_data')
   if teams:
      download_teams(data_dir, year)

   if drafts:
      download_draft(data_dir, year)

   if (league_id) and (league_id is not None):
      download_league(data_dir, league_id, year)


def download_teams(data_dir, year):

   teams = TeamData.Teams[year]

   for t in teams:
      print "downloading {0}, {1}".format(t, year)
      download_team(data_dir, t, year)
      time.sleep(10.0)


def download_draft(data_dir, year):

   data_dir = os.path.join(data_dir, "draft", str(year))
   mkdir_p(data_dir)

   filename = "draft.html"
   filename = os.path.join(data_dir, filename)

   fp = open(filename, "wb")
   curl = pycurl.Curl()
   curl.setopt(pycurl.URL, base_draft_url.format(year=year))
   curl.setopt(pycurl.FOLLOWLOCATION, 1)
   curl.setopt(pycurl.MAXREDIRS, 5)
   curl.setopt(pycurl.CONNECTTIMEOUT, 30)
   curl.setopt(pycurl.TIMEOUT, 300)
   curl.setopt(pycurl.NOSIGNAL, 1)
   curl.setopt(pycurl.WRITEDATA, fp)
   try:
      curl.perform()
   except pycurl.error:
      import traceback
      traceback.print_exc(file=sys.stderr)
   curl.close()
   fp.close()

   return


def download_team(data_dir, team, year=time.strftime('%Y', time.localtime())):

   data_dir = os.path.join(data_dir, "teams", str(year))
   mkdir_p(data_dir)

   filename = "{team}.html".format(team=team)
   filename = os.path.join(data_dir, filename)

   fp = open(filename, "wb")
   curl = pycurl.Curl()
   curl.setopt(pycurl.URL, base_team_url.format(team=team, year=year))
   curl.setopt(pycurl.FOLLOWLOCATION, 1)
   curl.setopt(pycurl.MAXREDIRS, 5)
   curl.setopt(pycurl.CONNECTTIMEOUT, 30)
   curl.setopt(pycurl.TIMEOUT, 300)
   curl.setopt(pycurl.NOSIGNAL, 1)
   curl.setopt(pycurl.WRITEDATA, fp)
   try:
      curl.perform()
   except pycurl.error:
      import traceback
      traceback.print_exc(file=sys.stderr)
   curl.close()
   fp.close()

   return


def download_league(data_dir, leagueID, year):
   """
      fetch standings and team data from espn.com
   """
   espn_pages = []

   league_dir = os.path.join(data_dir, 'league', str(year))
   mkdir_p(league_dir)

   leagueURL = "http://games.espn.go.com/fba/leaguerosters?" +\
               "leagueId={0}&seasonId={1}".format(leagueID, year)
   league_filename = "league.html"
   league_filename = os.path.join(league_dir, league_filename)
   espn_pages.append({'url': leagueURL, 'filename': league_filename})

   standingsURL = "http://games.espn.go.com/fba/standings?" +\
                  "leagueId={0}&seasonId={1}".format(leagueID, year)
   standings_filename = "standings.html"
   standings_filename = os.path.join(league_dir, standings_filename)
   espn_pages.append({'url': standingsURL, 'filename': standings_filename})

   draft_recap_url = 'http://games.espn.go.com/fba/tools/draftrecap?' +\
                     'leagueId={leagueID}&seasonId={year}'
   draft_recap_url = draft_recap_url.format(leagueID=leagueID, year=year)
   draft_recap_filename = "draft_recap.html"
   draft_recap_filename = os.path.join(league_dir, draft_recap_filename)
   espn_pages.append({'url': draft_recap_url,
                      'filename': draft_recap_filename})

   schedule_url = 'http://games.espn.go.com/fba/schedule?' +\
                  'leagueId={leagueID}&seasonId={year}'
   schedule_url = schedule_url.format(year=year, leagueID=leagueID)
   schedule_filename = "schedule.html"
   schedule_filename = os.path.join(league_dir, schedule_filename)
   espn_pages.append({'url': schedule_url, 'filename': schedule_filename})

   for page in espn_pages:
      fd = open(page['filename'], "w")

      c = pycurl.Curl()
      c.setopt(c.URL, page['url'])
      c.setopt(c.WRITEDATA, fd)

      try:
         c.perform()
      except pycurl.error:
         import traceback
         traceback.print_exc(file=sys.stderr)

      fd.close()

   c.close()
