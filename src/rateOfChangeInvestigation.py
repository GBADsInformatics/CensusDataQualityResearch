# Census Data Quality Research
# Written By Ian McKechnie
# Last Updated: Tuesday Feb 15, 2023

# We could take the average rate of change for the
# increase in a species population for each year for a
# given country for each data source. We could compare
# the rate of change between each data source and if
# one is substantially bigger than the other two it could
# be concluded that there is a higher chance that it is wrong.

#Answer is looking not great as not enough data to make a good conclusion. Each year has tops 2 countries with data for it

import API_helpers.fao as fao
import API_helpers.oie as oie
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import API_helpers.helperFunctions as helperFunctions
import plotly.figure_factory as ff
import numpy as np
import plotly.graph_objects as go

countries = ["Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]
species = ["Cattle","Sheep","Goats","Pigs","Chickens"]
specie = "Cattle"
country = "USA"

# Step one: Get FAO Data and OIE Data
if country == "USA":
    fao_data = fao.get_data("United%20States%20of%20America", specie)
    oie_data = oie.get_data("United%20States%20of%20America", specie)
else:
    fao_data = fao.get_data(country, specie)
    oie_data = oie.get_data(country, specie)

fao_data = fao.formatFAOData(fao_data)
oie_data = oie.formatOIEData(oie_data)

# Step 3: Get Census Data
csv_data, csv_index_list, species = helperFunctions.getFormattedCensusData(country, specie, species)

#Only get the rows that have the correct specie
new_csv_data = []
for index, row in csv_data.iterrows():
    if row['species'] == specie:
        new_csv_data.append( [row['year'], row['population']] )

csv_data = pd.DataFrame(new_csv_data, columns = ["year", "population"])

# Step 4: Get National Data
nationalData, nationalData_index_list, species = helperFunctions.getFormattedNationalData(country, specie, species)

new_national_data = []
for index, row in nationalData.iterrows():
    if row['species'] == specie:
        new_national_data.append( [row['year'], row['population']] )

nationalData = pd.DataFrame (new_national_data, columns = ["year", "population"])

# Get the rate of change of each point in each data set and put it into arrays
fao_roc = helperFunctions.getROC(fao_data, "population")
oie_roc = helperFunctions.getROC(oie_data, "population")
csv_roc = helperFunctions.getROC(csv_data, "population")
national_roc = helperFunctions.getROC(nationalData, "population")

# Step 5: Find the path distance between each point in each data set
mainDict = {}

# Get the only years that have multiple data points
fao_years = fao_roc.year.unique().tolist()
oie_years = oie_roc.year.unique().tolist()
csv_years = csv_roc.year.unique().tolist()
national_years = national_roc.year.unique().tolist()


#Make sure all data is strings
fao_years = [str(year) for year in fao_years]
oie_years = [str(year) for year in oie_years]
csv_years = [str(year) for year in csv_years]
national_years = [str(year) for year in national_years]

years = fao_years + oie_years + csv_years + national_years

years = list({x for x in years if years.count(x) > 1})
years.sort()

# Create the dictionary
for year in years:
    # This df is for each year in the table
    mainDf = pd.DataFrame(columns=["elen", "fao", "oie", "csv", "national"])

    # Set the elem column to fao
    fao_distances = ['fao']

    fao_dist = 0
    fao_year = 0

    #Get the fao roc for that year
    for value in fao_roc.values:
        if str(value[0]) == year:
            fao_dist = value[1]
            fao_year = str(value[0])

    if year == fao_year:

        #The fao column
        fao_distances.append(None)

        #The oie column
        for value in oie_roc.values:
            if str(value[0]) == year:
                fao_distances.append(fao_dist - value[1])
                break
        if len(fao_distances) == 2:
            fao_distances.append(None)

        #The csv column
        for value in csv_roc.values:
            if str(value[0]) == year:
                fao_distances.append(fao_dist - value[1])
                break
        if len(fao_distances) == 3:
            fao_distances.append(None)

        #The national column
        for value in national_roc.values:
            if str(value[0]) == year:
                fao_distances.append(fao_dist - value[1])
                break
        if len(fao_distances) == 4:
            fao_distances.append(None)

    else:
        fao_distances.append(None)
        fao_distances.append(None)
        fao_distances.append(None)
        fao_distances.append(None)

    mainDf.loc[0] = fao_distances

    # All the OIE distances
    oie_distances = ['oie']

    oie_dist = 0
    oie_year = 0

    for value in oie_roc.values:
        if str(value[0]) == year:
            oie_dist = value[1]
            oie_year = str(value[0])

    if year == oie_year:

        #The fao column
        for value in fao_roc.values:
            if str(value[0]) == year:
                oie_distances.append(value[1] - oie_dist)
                break
        if len(oie_distances) == 1:
            oie_distances.append(None)

        #The oie column
        oie_distances.append(None)

        #The csv column
        for value in csv_roc.values:
            if str(value[0]) == year:
                oie_distances.append(oie_dist - value[1])
                break
        if len(oie_distances) == 3:
            oie_distances.append(None)

        #The national column
        for value in national_roc.values:
            if str(value[0]) == year:
                oie_distances.append(oie_dist - value[1])
                break
        if len(oie_distances) == 4:
            oie_distances.append(None)

    else:
        oie_distances.append(None)
        oie_distances.append(None)
        oie_distances.append(None)
        oie_distances.append(None)

    mainDf.loc[1] = oie_distances


    # All the CSV distances
    csv_distances = ['csv']


    csv_dist = 0
    csv_year = 0

    for value in csv_roc.values:
        if str(value[0]) == year:
            csv_dist = value[1]
            csv_year = str(value[0])

    if year == csv_year:
        #The fao column
        for value in fao_roc.values:
            if str(value[0]) == year:
                csv_distances.append(value[1] - csv_dist)
                break
        if len(csv_distances) == 1:
            csv_distances.append(None)

        #The oie column
        for value in oie_roc.values:
            if str(value[0]) == year:
                csv_distances.append(csv_dist - value[1])
                break
        if len(csv_distances) == 2:
            csv_distances.append(None)

        #The csv column
        csv_distances.append(None)

        #The national column
        for value in national_roc.values:
            if str(value[0]) == year:
                csv_distances.append(csv_dist - value[1])
                break
        if len(csv_distances) == 4:
            csv_distances.append(None)

        #Set the column in the main df

    else:
        csv_distances.append(None)
        csv_distances.append(None)
        csv_distances.append(None)
        csv_distances.append(None)

    mainDf.loc[2] = csv_distances

    # All the National distances
    national_distances = ['national']

    national_dist = 0
    national_year = 0

    for value in national_roc.values:
        if str(value[0]) == year:
            national_dist = value[1]
            national_year = str(value[0])

    if year == national_year:
        #The fao column
        for value in fao_roc.values:
            if str(value[0]) == year:
                national_distances.append(value[1] - national_dist)
                break
        if len(national_distances) == 1:
            national_distances.append(None)

        #The oie column
        for value in oie_roc.values:
            if str(value[0]) == year:
                national_distances.append(national_dist - value[1])
                break
        if len(national_distances) == 2:
            national_distances.append(None)

        #The csv column
        for value in csv_roc.values:
            if str(value[0]) == year:
                national_distances.append(national_dist - value[1])
                break
        if len(national_distances) == 3:
            national_distances.append(None)

        #The national column
        national_distances.append(None)

    else:
        national_distances.append(None)
        national_distances.append(None)
        national_distances.append(None)
        national_distances.append(None)

    mainDf.loc[3] = national_distances

    # print("\n\nYear, ", year)
    # print("mainDf")
    # print(mainDf)

    mainDict[year] = mainDf

# print(mainDict)
for year in years:
    print("Year: ", year)
    print(mainDict[year])


# Need to use a network graph to visualize it
# app = Dash(__name__)

# app.layout = html.Div([
#     dcc.Graph(id='indicator-graphic'),

#     dcc.Slider(
#         year.min(),
#         year.max(),
#         step=None,
#         id='year--slider',
#         value=year.max(),
#         marks={str(year): str(year) for year in year},

#     )
# ])
