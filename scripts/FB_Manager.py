#!/usr/bin/env python
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

import os
import click
import errno


def mkdir_p(path):
   try:
      os.makedirs(path)
   except OSError as exc:
      if exc.errno == errno.EEXIST and os.path.isdir(path):
         pass
      else:
         raise


default_dir = os.path.expanduser("~/.fantasy_basketball")
default_raw_data_dir = os.path.join(default_dir, "raw_data")
default_processed_data_dir = os.path.join(default_dir, "processed_data")
default_html_dir = os.path.join(default_dir, "html")


@click.group()
def cli():
   pass


@cli.command()
@click.option('--data_dir',
              default=default_raw_data_dir,
              help='Download Fantasy Basketball Data')
def download(data_dir):
   mkdir_p(data_dir)
   click.echo('Downloading to {0}'.format(data_dir))


@cli.command()
@click.option('--data_dir',
              default=default_processed_data_dir,
              help='Process Fantasy Basketball Data')
def process(data_dir):
   mkdir_p(data_dir)
   click.echo('Processing to {0}'.format(data_dir))


@cli.command()
@click.option('--data_dir',
              default=default_html_dir,
              help='Process Fantasy Basketball Data')
def write_html(data_dir):
   mkdir_p(data_dir)
   click.echo('Writing HTML Data to {0}'.format(data_dir))


def main():
   cli()

   return

if __name__ == "__main__":
   main()
