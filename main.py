#importing libraries/packages

import fastf1 as ff1
#import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os

# Function to Check if the path specified is a valid directory
def isEmpty(path):
    if os.path.exists(path) and not os.path.isfile(path):
        # Checking if the directory is empty or not
        if not os.listdir(path):
            print("Empty directory")
            return 1
        else:
            print("Not empty directory")
            return 1
    else:
        print("The path is either for a file or not valid")
        return 0

Folder = "DriversHistoricData"
path = os.path.join(os.getcwd(),Folder)

FolderStatus =isEmpty(path)
if FolderStatus ==0:
    os.mkdir(path)

RaceDeets = {}

ff1.Cache.enable_cache(path)
EventYear = 2014
SeasonDetails = ff1.get_event_schedule(EventYear)
Cumm_points = {}
PointsDF = pd.DataFrame()

#Create New Folder for the year
EventFolder = str(EventYear)
EventFolderPath = os.path.join(os.getcwd(),EventFolder)
EventFolderStatus =isEmpty(EventFolderPath)
if EventFolderStatus ==0:
    os.mkdir(EventFolderPath)

os.chdir(EventFolderPath)


writer = pd.ExcelWriter("RacePoints_"+str(EventYear)+".xlsx")
#fetching Driver Points data for each Grand Prix
for i in range(len(SeasonDetails)):
    try:
        session = ff1.get_session(EventYear,i+1,'R')
        session.load()
        RaceDeets.update({session.event.EventName:{}})
        df = session.results
        Points= df[["FullName","Points"]]
        DF = pd.DataFrame(Points)
        #DF['Identifier'] = DF.index.values+DF["FullName"]
        DF['Identifier'] = DF["FullName"]
        DF=DF.set_index("Identifier",drop=True)
        DF.to_excel(writer,sheet_name=session.event.EventName)
        RaceDeets[session.event.EventName]= DF.to_dict()
    except Exception as e:
        print("Invalid Session, race number ",i," doesn't exist\n")
        print(e)
writer.save()
writer.close()

#intializing Driver Names with 0 points
DriversPoints = {drivers:0 for drivers in RaceDeets[session.event.EventName]['Points']}

for RaceDay in RaceDeets:
    Cumm_points[RaceDay] = {}
    for drivers in RaceDeets[RaceDay]["Points"]:
        try:
            DriversPoints[drivers] += RaceDeets[RaceDay]["Points"][drivers]
        except:
            DriversPoints[drivers] = 0.0
            DriversPoints[drivers] += RaceDeets[RaceDay]["Points"][drivers]
    Cumm_points[RaceDay]= {keys:DriversPoints[keys] for keys in DriversPoints}

CummDF = pd.DataFrame(Cumm_points).fillna(0).transpose()
CummDF.to_excel(str(EventYear)+"_CummulativePoints.xlsx")
TopTen = CummDF[CummDF.loc[CummDF.index[len(CummDF)-1]].sort_values(ascending=False).index.values[:10]]
TopTen.plot(kind="line")
plt.show()
plt.savefig(str(EventYear)+"_PointsGraph.png")
print(Cumm_points)

