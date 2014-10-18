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
import errno

from Util import mkdir_p

import matplotlib.pyplot as plt


class Plotter(object):

   def __init__(self, data_dir, year):
      default_processed_data_dir = os.path.join(data_dir, 'processed_data')
      default_plot_dir = os.path.join(data_dir, 'plots')
      self.save_dir = os.path.join(default_plot_dir, year)
      fname = os.path.join(default_processed_data_dir, year, 'team_data.pkl')

      self.df = pd.read_pickle(fname)
      self.year = year

      self.make_positional_df()

      mkdir_p(self.save_dir)

   def make_positional_df(self):
      self.C = self.df[self.df.Pos == 'C']
      self.PF = self.df[self.df.Pos == 'PF']
      self.SF = self.df[self.df.Pos == 'SF']
      self.SG = self.df[self.df.Pos == 'SG']
      self.PG = self.df[self.df.Pos == 'PG']

   def is_plot_func(self, s):
      if re.search("^plot_", s) is not None:
         attr = getattr(self, s)
         if callable(attr):
            return True

      return False

   def make_all_plots(self, img_format='eps'):

      attrs = dir(self)

      plot_funcs = [x for x in attrs if self.is_plot_func(x)]

      for func in plot_funcs:
         f = getattr(self, func)
         f(img_format)


