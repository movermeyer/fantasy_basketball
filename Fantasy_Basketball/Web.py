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
import pandas as pd
import fnmatch
from Util import mkdir_p
from jinja2 import Environment, FileSystemLoader


class Web(object):
   """
      :raises IOError:

   """

   def __init__(self, data_dir):

      self.data_dir = data_dir
      self.processed_dir = os.path.join(self.data_dir, "processed_data")
      self.plots_dir = os.path.join(self.data_dir, 'plots')
      if not os.path.isdir(self.data_dir):
         raise IOError("{0} not a valid directory".format(self.data_dir))
      self.dataframes = []
      self.pages = []

      j2_env = Environment(loader=FileSystemLoader('templates'),
                           trim_blocks=True)
      self.baseTemplate = j2_env.get_template('fantasy-template.html')
      self.tocTemplate = j2_env.get_template('toc.html')
      self.posTemplate = j2_env.get_template('positional-template.html')
      self.chartsTemplate = j2_env.get_template('charts-template.html')

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

      self.write_html()

   def find_data(self):
      """

      """
      self.years = []
      matches = []
      for root, _, filenames in os.walk(self.processed_dir):
         for filename in fnmatch.filter(filenames, '*.pkl'):
            year = re.sub(r'^' + self.processed_dir, '', root)
            year = re.sub(r'^/', '', year)
            year = re.sub(r'/$', '', year)
            year = int(year)
            self.years.append(year)

            # If these dataframes get to be too big maybe just store the path
            # instead of all the data
            df = pd.read_pickle(os.path.join(root, filename))
            if 'team_data' in filename:
               data_type = 'team_data'
            else:
               data_type = 'other'
            match = {'year': year, 'df': df, 'data_type': data_type}
            matches.append(match)

      self.years = list(set(self.years))

      self.data = matches

      matches = []
      for root, dirnames, filenames in os.walk(self.plots_dir):
         for filename in fnmatch.filter(filenames, '*.json'):
            year = re.sub(r'^' + self.plots_dir, '', root)
            year = re.sub(r'^/', '', year)
            year = re.sub(r'/$', '', year)
            year = int(year)

            match = {'year': year, 'plot_file': filename}
            matches.append(match)

      self.plot_data = matches

   def add_page_player_value(self):
      """

      """
      for data_item in self.data:
         df = data_item['df']
         year = str(data_item['year'])
         p = {'title': 'Value Data',
              'year': year,
              'obj': df,
              'table_id': 'value',
              'href': 'value-data.html',
              'cols': ['Player', 'Pos',
                       'GS', 'MP', 'FG%', 'FT%', '3P', 'TRB', 'AST', 'STL',
                       'BLK', 'PTS', 'Salary', 'value', 'price'],
              'template': self.posTemplate}
         self.pages.append(p)

      return

   def write_html(self):
      """
         This needs a re-write
      """
      html_dir = os.path.join(self.data_dir, 'html')
      mkdir_p(html_dir)

      for p in self.pages:
         dump_html_dir = os.path.join(html_dir, str(p['year']))
         mkdir_p(dump_html_dir)

         with open(os.path.join(dump_html_dir, p['href']), 'w') as fd:
            text = self.render_tables(p)
            fd.write(text.encode('UTF-8'))

      self.render_plots()

      self.render_toc()

   def render_plots(self):
      '''

      '''
      years = [ii['year'] for ii in self.plot_data]
      html_dir = os.path.join(self.data_dir, 'html')
      data = self.plot_data

      for year in years:
         plots_dir = os.path.join(html_dir, str(year))
         mkdir_p(plots_dir)

         # Filter all plots by year
         plot_files = [ii for ii in data if ii['year'] == year]

         with open(os.path.join(plots_dir, 'plots.html'), 'w') as fd:
            text = self.chartsTemplate.render(title='Plots',
                                              years=self.years,
                                              plots=plot_files)
            fd.write(text.encode('UTF-8'))

   def render_toc(self):
      '''
      FIXME rewrite this
      '''
      html_dir = os.path.join(self.data_dir, 'html')
      mkdir_p(html_dir)

      with open(os.path.join(html_dir, 'toc.html'), 'w') as fd:
         text = self.tocTemplate.render(title='Table of Contents',
                                        pages=self.pages,
                                        years=self.years,
                                        allPages=self.pages)
         fd.write(text.encode('UTF-8'))

   def render_tables(self, p):
      '''

      '''
      htmlText = p['obj'].to_html(columns=p['cols'],
                                  classes=['table', 'table-bordered'])
      htmlText = re.sub(r'^<table border',
                        r'<table id="sorter_class" border',
                        htmlText)

      template = p['template']
      text = template.render(title=p['title'],
                             fantasy_table=unicode(htmlText),
                             table_id=p['table_id'],
                             class_id='sorter_class',
                             year=p['year'],
                             years=self.years,
                             allPages=self.pages)

      return text
