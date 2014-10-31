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

import os
from bs4 import BeautifulSoup
import pandas as pd
from Util import mkdir_p


class ESPN(object):

   def __init__(self, data_dir, year, leagueID):
      """
         init ESPN object

         :param year: The year that league takes place
         :param leagueID: The ESPN league ID
      """

      self.year = year
      self.leagueID = leagueID

      self.data_dir = data_dir
      self.league_dir = os.path.join(self.data_dir,
                                     'raw_data',
                                     'league',
                                     str(self.year))

      self.processLeague()
      self.write_pkl()

   def write_pkl(self):
      """

      """
      dst_dir = os.path.join(self.data_dir,
                             'processed_data',
                             str(self.year))
      mkdir_p(dst_dir)
      dst_file= os.path.join(dst_dir, 'league_data.pkl')
      self.df.to_pickle(dst_file)


   def processLeague(self):
      """
         extract info from standings and league info, place into dataframe
      """

      self.process_standings()

   def process_standings(self):
      """

      """

      filename = os.path.join(self.league_dir, 'standings.html')
      with open(filename, 'r') as fd:
         soup = BeautifulSoup(fd)

      df1 = self.process_standings_table_1(soup)
      df2 = self.process_standings_table_2(soup)

      self.df = pd.merge(df1, df2, on='name')

   def process_standings_table_1(self, soup):
      """

      """

      tables = soup.findAll("table")
      data = []

      for table in tables:
         if table.findAll(text='EAST'):
            east = table
         if table.findAll(text='WEST'):
            west = table

      teams = east.findAll('tr')[2:]
      for t in teams:
         cols = t.findAll('td')
         d = {}
         d['wins'] = int(cols[1].text)
         d['losses'] = int(cols[2].text)
         d['ties'] = int(cols[3].text)
         d['pct'] = float(cols[4].text)
         if cols[5].text == '--':
            d['gb'] = 0
         else:
            d['gb'] = float(cols[5].text)
         d['conf'] = 'east'
         teamName = (cols[0].text)
         d['name'] = teamName
         data.append(d)

      teams = west.findAll('tr')[2:]
      for t in teams:
         cols = t.findAll('td')
         d = {}
         d['wins'] = int(cols[1].text)
         d['losses'] = int(cols[2].text)
         d['ties'] = int(cols[3].text)
         d['pct'] = float(cols[4].text)
         if cols[5].text == '--':
            d['gb'] = 0
         else:
            d['gb'] = float(cols[5].text)
         d['conf'] = 'west'
         teamName = (cols[0].text)
         d['name'] = teamName
         data.append(d)

      df = pd.DataFrame(data)

      return df

   def process_standings_table_2(self, soup):

      all_teams = soup.findAll('table', {'id': 'statsTable'})
      all_teams = all_teams[0]

      rows = all_teams.findAll('tr')
      rows = rows[3:]  # the first three rows are fluff

      teams = []
      for row in rows:
         d = {}
         cols = row.findAll('td')

         d['rank'] = int(cols[0].text)
         d['name'] = cols[1].text
         d['FG%'] = float(cols[3].text)
         d['FT%'] = float(cols[4].text)
         d['3PM'] = int(cols[5].text)
         d['REB'] = int(cols[6].text)
         d['AST'] = int(cols[7].text)
         d['STL'] = int(cols[8].text)
         d['BLK'] = int(cols[9].text)
         d['PTS'] = int(cols[10].text)
         d['TW'] = int(cols[11].text)

         # ESPN changed their table format... thanks!
         try:
            d['moves'] = int(cols[14].text)
         except IndexError:
            d['moves'] = int(cols[13].text)

         teams.append(d)

      df = pd.DataFrame(teams)
      return df

   def process_something_else(self):

      soup = BeautifulSoup(self.leagueBuf.getvalue())
      tables = soup.findAll("table", attrs={"class": "playerTableTable"})
      for table in tables:
         teamName = table.findAll('tr')[0].findAll('a')[0].text
         teamName = teamName.lower()
         rows = table.findAll('tr')[2:]
         players = []
         for row in rows:
            try:
               player = row.findAll('a')[0].text
               players.append(player)
            except IndexError:
               pass

         self.teams[teamName]['players'] = players
