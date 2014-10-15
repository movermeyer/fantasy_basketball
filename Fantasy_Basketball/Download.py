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

base_draft_url = "http://www.basketball-reference.com/draft/NBA_{year}.html"
base_team_url = "http://www.basketball-reference.com/teams/{team}/{year}.html"


def downloadDrafts():

   years = range(1950, 2014)
   years.reverse()

   for y in years:
      downloadDraft(y)
      time.sleep(10.0)


def downloadTeams():

   teams = [u'SAS', u'OKC', u'CHI', u'BOS', u'PHO', u'MEM', u'ORL', u'NYK',
            u'PHI', u'NOH', u'UTA', u'ATL', u'DEN', u'IND', u'HOU', u'SAC',
            u'CHA', u'LAL', u'DET', u'BRK', u'MIN', u'GSW', u'TOR', u'POR',
            u'WAS', u'LAC', u'MIA', u'MIL', u'CLE', u'DAL']

   for y in ['2013', '2014', '2012']:
      for t in teams:
         print "downloading {0}, {1}".format(t, y)
         downloadTeam(t, y)
         time.sleep(10.0)


def downloadDraft(data_dir, year):

   filename = "{0}/draft_{1}.html".format(data_dir, year)
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
   except:
      import traceback
      traceback.print_exc(file=sys.stderr)
   curl.close()
   fp.close()

   return


def downloadTeam(team, year=time.strftime('%Y', time.localtime())):

   filename = "{data_dir}/{team}_{year}.html".format(data_dir=data_dir,
                                                     team=team,
                                                     year=year)
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
   except:
      import traceback
      traceback.print_exc(file=sys.stderr)
   curl.close()
   fp.close()

   return
