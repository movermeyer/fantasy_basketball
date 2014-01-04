#!/usr/bin/env python

__author__ = "Devin Kelly"

import copy
import pycurl
import cStringIO
import re
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', None)
pd.set_option('display.precision', 4)
htmlRoot = "html/"
minimumMinutesPlayed = 200


class ESPN(object):

   def __init__(self):
      """init ESPN object"""
      leagueID = 67955
      year = 2014
      self.leagueURL = "http://games.espn.go.com/fba/leaguerosters?leagueId={0}&seasonID={1}".format(leagueID, year)
      self.standingsURL = "http://games.espn.go.com/fba/standings?leagueId={0}&seasonID={1}".format(leagueID, year)

      self.downloadLeague()
      self.processLeague()

   def downloadLeague(self):
      """fetch standings and team data from espn.com"""
      self.leagueBuf = cStringIO.StringIO()
      self.standingsBuf = cStringIO.StringIO()

      c = pycurl.Curl()
      c.setopt(c.URL, self.leagueURL)
      c.setopt(c.WRITEFUNCTION, self.leagueBuf.write)
      c.perform()

      c.setopt(c.URL, self.standingsURL)
      c.setopt(c.WRITEFUNCTION, self.standingsBuf.write)
      c.perform()

   def processLeague(self):
      """extract info from standings and league info, place into dataframe"""

      self.teams = {}
      soup = BeautifulSoup(self.standingsBuf.getvalue())
      tables = soup.findAll("table")

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
         d['conf'] = 'east'
         teamName = (cols[0].text).lower()
         self.teams[teamName] = d

      teams = west.findAll('tr')[2:]
      for t in teams:
         cols = t.findAll('td')
         d = {}
         d['wins'] = int(cols[1].text)
         d['losses'] = int(cols[2].text)
         d['ties'] = int(cols[3].text)
         d['conf'] = 'west'
         teamName = (cols[0].text).lower()
         self.teams[teamName] = d

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
            except:
               pass

         self.teams[teamName]['players'] = players


class RawStats(object):

   def __init__(self):
      self.url = "www.basketball-reference.com/leagues/NBA_2014_totals.html"
      self.csvName = 'nba_stats.csv'
      self.columns = ['', 'Rk', 'Player', 'Pos', 'Age', 'Tm', 'G', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', '2P', '2PA', '2P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'FTeam']

      if not os.path.isfile(self.csvName):
         self.downloadHTML()
         self.processHTML()
         self.writeCSV()
      else:
         self.data = pd.read_csv(self.csvName)
         self.data.columns = self.columns

      self.data.fillna(0.0)
      replacement = {"Pos": {'PF-SF': 'PF', 'PG-SG': 'PG', 'PG-SG': 'PG', 'SF-PF': 'SF', 'SF-SG': 'SF', '^G$': 'SG'}}
      self.data.replace(to_replace=replacement, inplace=True, regex=True)

      return

   def writeCSV(self):
      self.data.to_csv(self.csvName)  # , cols=self.columns)  # FIXME -- do we need cols=self.coloumns

   def downloadHTML(self):
      self.buf = cStringIO.StringIO()
      c = pycurl.Curl()
      c.setopt(c.URL, self.url)
      c.setopt(c.WRITEFUNCTION, self.buf.write)
      c.perform()


   def processHTML(self):
      """ Finds the table in the downloaded HTML and converts it into a CSV """

      soup = BeautifulSoup(self.buf.getvalue())
      table = soup.find("table")

      thead = table.findAll("thead")[0]
      tbody = table.findAll("tbody")[0]

      labels = [th.getText() for th in thead.findAll("th")]
      rows = tbody.findAll("tr")

      self.stats = pd.DataFrame(columns=labels)

      tmpStats = []

      for row in rows:
         if row.find('th') is not None:
            continue
         vals = [td.getText() for td in row.findAll("td")]
         vals = [0 if w == '' else w for w in vals]  # if no statistic, fill with 0
         tmpStats.append(dict(zip(labels, vals)))

      self.data = pd.DataFrame(columns=labels, data=tmpStats, dtype=float)
      self.data = self.data[self.data.MP > minimumMinutesPlayed]
      self.data[u'FTeam'] = 'FA'


class Stats(object):

   def __init__(self, data, filesPath=htmlRoot):

      self.data = data
      self.filesPath = filesPath
      self.addNaiveValue()
      self.addNormalizedValue()
      self.rank()
      self.displayData = ['Player', 'Pos', 'Tm', 'G', 'GS', 'MP', 'FG%', 'FT%', 'TRB', 'AST', 'STL', 'BLK', 'PTS', 'FTeam']
      return

   def addNaiveValue(self):

      stats = ['FG%', 'FT%', 'TRB', 'AST', 'BLK', 'PTS']
      M = self.data.max(axis=0)
      maxStats = [M[s] for s in stats]
      maxDict = dict(zip(stats, maxStats))

      M = self.data.min(axis=0)
      minStats = [M[s] for s in stats]
      minDict = dict(zip(stats, minStats))

      self.data['NaiveValue'] = (self.data['FG%'] - float(minDict['FG%'])) / float(maxDict['FG%']) + \
                                (self.data['FT%'] - float(minDict['FG%'])) / float(maxDict['FT%']) + \
                                (self.data['TRB'] - float(minDict['TRB'])) / float(maxDict['TRB']) + \
                                (self.data['AST'] - float(minDict['AST'])) / float(maxDict['AST']) + \
                                (self.data['BLK'] - float(minDict['BLK'])) / float(maxDict['BLK']) + \
                                (self.data['PTS'] - float(minDict['PTS'])) / float(maxDict['PTS'])

      self.data = self.data[np.isfinite(self.data.NaiveValue)]

   def addNormalizedValue(self):
      self.data['NormalizedValue'] = (self.data['FG%'] - self.data['FG%'].mean()) / self.data['FG%'].std() + \
                                     (self.data['FT%'] - self.data['FG%'].mean()) / self.data['FT%'].std() + \
                                     (self.data['TRB'] - self.data['TRB'].mean()) / self.data['TRB'].std() + \
                                     (self.data['AST'] - self.data['AST'].mean()) / self.data['AST'].std() + \
                                     (self.data['BLK'] - self.data['BLK'].mean()) / self.data['BLK'].std() + \
                                     (self.data['PTS'] - self.data['PTS'].mean()) / self.data['PTS'].std()

   def addPositionalMean(self):
      positionBreakdown = self.data.groupby('Pos')
      self.pbMean = positionBreakdown.mean()
      self.spreads = self.pbMean.max() - self.pbMean.min()

   def addPositionalData(self):
      self.positional = self.data.groupby('Pos')
      self.positional.fillna(self.positional.mean(), inplace=True)
      self.positional.dropna()

   def makeRosters(self):
      self.rosters = copy.deepcopy(self.data)
      self.rosters = self.rosters[self.rosters['FTeam'] != 'FA']
      self.rosters = self.rosters.groupby('FTeam')

   def addValueByTeam(self):

      self.teamValue = self.rosters.mean()

   def makePlots(self):
      plotItems = ['NaiveValue', 'NormalizedValue', 'FG%', 'FT%', 'TRB', 'AST', 'BLK', 'STL', 'PTS']
      self.figures = []
      for ii in plotItems:
         plt.figure()
         self.data[ii].hist(bins=50)
         plt.title(ii)
         fName = "{0}.png".format(ii)
         fName = re.sub("%", "", fName)
         fPath = os.path.join(self.filesPath, fName)
         plt.savefig(fPath)
         plt.close()
         self.figures.append({"title": ii, "filePath": fPath, "fileName": fName})

   def rank(self):
      self.data['rank'] = self.data['NormalizedValue'].rank(ascending=False)
      self.data.sort('rank', inplace=True)

   def addFantasyTeams(self, teams):

      for k in teams.keys():
         for player in teams[k]['players']:
            #self.data[self.data['Player'] == player].FTeam = k
            self.data.FTeam[self.data.Player == player] = k

      return

   def writeHTML(self):
      j2_env = Environment(loader=FileSystemLoader('templates'), trim_blocks=True)
      baseTemplate = j2_env.get_template('fantasy-template.html')
      tocTemplate = j2_env.get_template('toc.html')
      posTemplate = j2_env.get_template('positional-template.html')
      chartsTemplate = j2_env.get_template('charts-template.html')

      pages = []
      pages.append({'title': 'Value Data',
                    'obj': self.data,
                    'fantasyID': 'value',
                    'href': 'value-data.html',
                    'cols': ['rank', 'Player', 'Pos', 'FTeam', 'Tm', 'G', 'GS', 'MP', 'FG%', 'FT%', 'TRB', 'AST', 'STL', 'BLK', 'PTS', 'NormalizedValue', 'NaiveValue']})
      pages.append({'title': 'Value by Position',
                    'obj': self.positional,
                    'fantasyID': 'normalized-value-positional',
                    'href': 'normalized-value-positional.html',
                    'cols': ['Player', 'Pos', 'FTeam', 'Tm', 'G', 'GS', 'MP', 'FG%', 'FT%', 'TRB', 'AST', 'STL', 'BLK', 'PTS', 'NormalizedValue', 'NaiveValue']})
      pages.append({'title': 'Positional Breakdown By Mean',
                    'obj': self.pbMean,
                    'fantasyID': 'pb-mean',
                    'href': 'pb-mean.html',
                    'cols': ['G', 'GS', 'MP', 'FG%', 'FT%', 'TRB', 'AST', 'STL', 'BLK', 'PTS', 'NormalizedValue', 'NaiveValue']})
      pages.append({'title': 'Team Average Value',
                    'obj': self.teamValue,
                    'fantasyID': 'teamValue',
                    'href': 'teamValue.html',
                    'cols': ['G', 'GS', 'MP', 'FG%', 'FT%', 'TRB', 'AST', 'STL', 'BLK', 'PTS', 'NormalizedValue', 'NaiveValue']})
      pages.append({'title': 'Rosters',
                    'obj': self.rosters,
                    'fantasyID': 'rosters',
                    'href': 'rosters.html',
                    'cols': ['rank', 'Player', 'Pos', 'FTeam', 'Tm', 'G', 'GS', 'MP', 'FG%', 'FT%', 'TRB', 'AST', 'STL', 'BLK', 'PTS', 'NormalizedValue', 'NaiveValue']})

      expr1 = re.compile(r"<tr>.*rank.*</thead>",  re.MULTILINE | re.DOTALL)
      expr2 = re.compile(r"<tr>.*Pos.*</thead>",  re.MULTILINE | re.DOTALL)
      expr3 = re.compile(r"<tr>.*FTeam.*</thead>",  re.MULTILINE | re.DOTALL)
      for p in pages:
         fantasyID = p['fantasyID']
         htmlText = p['obj'].to_html(columns=p['cols'], classes=["table", "table-bordered"])

         if fantasyID == 'pb-mean':
            expr = expr2
         elif fantasyID == 'teamValue':
            expr = expr3
         else:
            expr = expr1

         if ('normalized-value-positional' == fantasyID) or ('rosters' == fantasyID):
            for k in htmlText.keys():
               newKey = re.sub(r'\s', '_', k)
               newKey = re.sub(r'\+', '_', newKey)
               htmlText.rename({k: newKey}, inplace=True)

            for k in htmlText.keys():
                  htmlText[k] = htmlText[k][:7] + 'id="{0}" '.format(k) + htmlText[k][7:]
                  htmlText[k] = re.sub(expr, "</thead>", htmlText[k])
            template = posTemplate
         else:
            htmlText = htmlText[:7] + 'id="{0}" '.format(fantasyID) + htmlText[7:]
            htmlText = re.sub(expr, "</thead>", htmlText)
            template = baseTemplate

         with open(os.path.join(self.filesPath, p['href']), 'w') as fd:
            text = template.render(title=p['title'],
                                   fantasy_table=htmlText,
                                   fantasy_id=fantasyID)
            fd.write(text)

         with open(os.path.join(self.filesPath, 'charts.html'), 'w') as fd:
            text = chartsTemplate.render(title='Charts', figs=self.figures)
            fd.write(text)

         with open(os.path.join(self.filesPath, 'toc.html'), 'w') as fd:
            text = tocTemplate.render(title='Table of Contents', pages=pages, chartsUrl='charts.html')
            fd.write(text)


def main():

   espn = ESPN()
   rs = RawStats()
   stats = Stats(rs.data)
   stats.addFantasyTeams(espn.teams)
   stats.addPositionalMean()
   stats.addPositionalData()
   stats.makeRosters()
   stats.addValueByTeam()
   stats.makePlots()
   stats.writeHTML()

   return

if __name__ == "__main__":
   main()
