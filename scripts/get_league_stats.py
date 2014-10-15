
from Fantasy_Basketball import ESPN_League
from Fantasy_Basketball import Raw_Stats
from Fantasy_Basketball import Stats


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
