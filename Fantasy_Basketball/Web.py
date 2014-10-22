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
import re
import fnmatch
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from jinja2 import Environment, FileSystemLoader


class Web(object):
   """
      :raises IOError:

   """

   def __init__(self, data_dir):

      self.data_dir = data_dir
      self.processed_dir = os.path.join(self.data_dir, "processed_data")
      if not os.path.isdir(self.data_dir):
         raise IOError("{0} not a valid directory".format(self.data_dir))
      self.dataframes = []
      self.pages = []

   def gen_html(self):

      self.find_data()
      self.make_all_pages()

   def is_add_page_func(self, s):
      if re.search("^add_page_", s) is not None:
         attr = getattr(self, s)
         if callable(attr):
            return True

      return False

   def make_all_pages(self):

      attrs = dir(self)

      gen_page_funcs = [x for x in attrs if self.is_add_page_func(x)]

      for func in gen_page_funcs:
         f = getattr(self, func)
         f()

      write_html()

   def find_data(self):
      """

      """
      matches = []
      for root, dirnames, filenames in os.walk(self.processed_dir):
         for filename in fnmatch.filter(filenames, '*.pkl'):
            year = re.sub(r'^' + self.processed_dir, '', root)
            year = re.sub(r'^/', '', year)
            year = re.sub(r'/$', '', year)
            year = int(year)

            # If these dataframes get to be too big maybe just store the path
            # instead of all the data
            df = pd.read_pickle(os.path.join(root, filename))
            if 'team_data' in filename:
               data_type = 'team_data'
            else:
               data_type = 'other'
            match = {'year': year, 'df': df, 'data_type': data_type}
            matches.append(match)

      self.data = matches

   def add_page_player_value(self):
      """

      """
      for data_item in self.data:
         df = data_item['df']
         year = str(data_item['year'])
         p = {'title': 'Value Data',
              'year': year,
              'obj': df,
              'fantasyID': 'value',
              'href': 'value-data.html',
              'cols': ['Player', 'Pos', 'FTeam', 'Tm', 'G',
                       'GS', 'MP', 'FG%', 'FT%', 'TRB', 'AST', 'STL',
                       'BLK', 'PTS', 'NormalizedValue']}
         self.pages.append(p)

      self.gen_index()
      return

   def add_page_images(self):
      """

      """
      self.gen_index()
      return

   def gen_index(self):
      """

      """

      return

   def write_html(self):
      """
         This needs a re-write
      """
      j2_env = Environment(loader=FileSystemLoader('templates'),
                           trim_blocks=True)
      baseTemplate = j2_env.get_template('fantasy-template.html')
      tocTemplate = j2_env.get_template('toc.html')
      posTemplate = j2_env.get_template('positional-template.html')
      chartsTemplate = j2_env.get_template('charts-template.html')

      expr1 = re.compile(r"<tr>.*rank.*</thead>", re.MULTILINE | re.DOTALL)
      expr2 = re.compile(r"<tr>.*Pos.*</thead>", re.MULTILINE | re.DOTALL)
      expr3 = re.compile(r"<tr>.*FTeam.*</thead>", re.MULTILINE | re.DOTALL)

      for p in pages:
         fantasyID = p['fantasyID']
         htmlText = p['obj'].to_html(columns=p['cols'],
                                     classes=["table", "table-bordered"])

         if fantasyID == 'pb-mean':
            expr = expr2
         elif fantasyID == 'teamValue':
            expr = expr3
         else:
            expr = expr1

         tmp = ('normalized-value-positional' == fantasyID) or \
               ('rosters' == fantasyID)

         if tmp:
            for k in htmlText.keys():
               newKey = re.sub(r'\s', '_', k)
               newKey = re.sub(r'\+', '_', newKey)
               htmlText.rename({k: newKey}, inplace=True)

            for k in htmlText.keys():
                  txt = htmlText[k][:7]
                  htmlText[k] = txt
                  htmlText[k] += 'id="{0}" '.format(k)
                  htmlText[k] += txt
                  htmlText[k] = re.sub(expr, "</thead>", htmlText[k])
            template = posTemplate
         else:
            s = htmlText[:7]
            htmlText = s + 'id="{0}" '.format(fantasyID) + s
            htmlText = re.sub(expr, "</thead>", htmlText)
            template = baseTemplate

         with open(os.path.join(self.filesPath, p['href']), 'w') as fd:
            text = template.render(title=p['title'],
                                   fantasy_table=htmlText,
                                   fantasy_id=fantasyID,
                                   allPages=pages)
            fd.write(text)

         with open(os.path.join(self.filesPath, 'charts.html'), 'w') as fd:
            text = chartsTemplate.render(title='Charts',
                                         figs=self.figures,
                                         allPages=pages)
            fd.write(text)

         with open(os.path.join(self.filesPath, 'toc.html'), 'w') as fd:
            text = tocTemplate.render(title='Table of Contents',
                                      pages=pages,
                                      chartsUrl='charts.html',
                                      allPages=pages)
            fd.write(text)
