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


def plot_stats(data_dir, year):
   default_processed_data_dir = os.path.join(data_dir, 'processed_data')
   default_plot_dir = os.path.join(data_dir, 'plots')
   save_dir = os.path.join(default_plot_dir, year)
   fname = os.path.join(default_processed_data_dir, year, 'team_data.pkl')

   df = pd.read_pickle(fname)
   plot_value_hist(save_dir, df)


def plot_value_hist(save_dir, df, img_format="eps"):

   year = list(set(df['year']))[0]
   mkdir_p(save_dir)

   df.hist('value', bins=20)

   fig = plt.gcf()
   fig.savefig(os.path.join(save_dir, "value_histogram.".format(img_format)))
