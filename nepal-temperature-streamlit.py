#Importing necessary libraries
import xarray as xr #helps work with NetCDF files
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import linregress

#Setting the layout of streamlit to wide
st.set_page_config(layout="wide")

#Getting the data
df_monthly_temp = pd.read_csv(r"year_monthly_temp_1940_2024.csv")

#Adding a dropdown to select the years to display on the chart
years = sorted(df_monthly_temp['year'].unique())
selected_years = st.multiselect(
    "Select year(s) to display",
    options=years,
    default=[2020, 2021, 2022, 2023, 2024]  # show all years at start
)

#Starting by initializing plotly figure to add parts to
fig1 = go.Figure()

month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] # To replace the numbers 1-12


#Lines for older years and making them all grey (1940–2019)
prev_years_0 = list(range(1940, 2020))
prev_years = []

for i in prev_years_0:
    if i in selected_years:
        prev_years.append(i)
for i, year in enumerate(sorted(prev_years)):
    #For each year, getting the 12 month temperatures
    yearly_data = df_monthly_temp[df_monthly_temp['year'] == year]
    #Getting actual months instead of numbers from 1-12
    months = [month_names[m-1] for m in yearly_data['month']]
    #Getting the temperature values (C) for selected month
    temperature = yearly_data['monthly_temperature_C']
    
    #Since all years from 1940 to 2019 have the same properties, adding only one legend entry for 1940–2019
    show_legend = True if i == 0 else False
    fig1.add_trace(go.Scatter(
        x = months, y = temperature,
        mode = 'lines',
        line = dict(color = 'grey', width = 1.5),
        opacity = 0.3,
        name = "1940 – 2019" if show_legend else None,
        showlegend=show_legend,
        hovertemplate=
            '<b>Year:</b> %{text}<br>' +
            '<b>Month:</b> %{x}<br>' +
            '<b>Temp:</b> %{y:.2f} °C<extra></extra>',
        text=[str(year)] * len(months) 
    ))

#Lines for more recent years and making them different colors and more bolder (2020–2023, dashed thick lines)

new_years_0 = [2020, 2021, 2022, 2023]

new_years = []

for i in new_years_0:
    if i in selected_years:
        new_years.append(i)
new_colors = {2020: "red", 2021: "blue", 2022: "green", 2023: "orange"}
for year in new_years:
    yearly_data = df_monthly_temp[df_monthly_temp['year'] == year]
    months = [month_names[m-1] for m in yearly_data['month']]
    temperature = yearly_data['monthly_temperature_C']
    
    fig1.add_trace(go.Scatter(
        x = months, y = temperature,
        mode = 'lines',
        line = dict(dash = 'dash', width = 5, color = new_colors[year]),
        opacity = 0.7,
        name = str(year),
        hovertemplate=
            '<b>Year:</b> %{text}<br>' +
            '<b>Month:</b> %{x}<br>' +
            '<b>Temp:</b> %{y:.2f} °C<extra></extra>',
        text=[str(year)] * len(months) 
    ))

#Line for most recent year 2024, making it bold and black
if 2024 in selected_years:
    year = 2024
    yearly_data = df_monthly_temp[df_monthly_temp['year'] == year]
    months = [month_names[m-1] for m in yearly_data['month']]
    temperature = yearly_data['monthly_temperature_C']

    fig1.add_trace(go.Scatter(
        x = months, y = temperature,
        mode = 'lines',
        line = dict(dash = 'longdash', width = 8, color = 'black'),
        opacity = 0.9,
        name = str(year),
        hovertemplate=
                '<b>Year:</b> %{text}<br>' +
                '<b>Month:</b> %{x}<br>' +
                '<b>Temp:</b> %{y:.2f} °C<extra></extra>',
            text=[str(year)] * len(months) 
    ))

#Overall layout for the graph
fig1.update_layout(
    title="Monthly Temperature of Nepal (1940 to 2024)",
    title_font=dict(size=24, family="Calibri", color="black", weight = 'bold'),  # bold title
    xaxis=dict(
        title="Month",
        title_font=dict(size=22, family="Calibri", color="black", weight = 'bold'),  # bold axis label
        tickfont=dict(size=18, family="Calibri", color="black", weight = 'bold')     # bold ticks
    ),
    yaxis=dict(
        title="Temperature (°C)",
        title_font=dict(size=22, family="Calibri", color="black", weight = 'bold'),  # bold axis label
        tickfont=dict(size=18, family="Calibri", color="black", weight = 'bold')     # bold ticks
    ),
    legend=dict(
        title="Year",
        title_font=dict(size=18, family="Calibri", color="black", weight = 'bold'), # bold legend title
        font=dict(size=16, family="Calibri", color="black", weight = 'bold')        # bold legend items
    ),
    template="plotly_white",
    width=1400, height=750
)

#Displaying the chart
st.plotly_chart(fig1, use_container_width=True)



#Getting a datetime column for each year and month and their avg temps
df_monthly_temp['date'] = df_monthly_temp['year'].astype(str) + '-' + df_monthly_temp['month'].astype(str) + '-01'
df_monthly_temp['date'] = pd.to_datetime(df_monthly_temp['date'], format = '%Y-%m-%d')

#Getting a decade column (will be the start of the decade)
df_monthly_temp['decade'] = (df_monthly_temp['date'].dt.year // 10) * 10

#Getting the decade average temperatures in a new table
decade_avg = df_monthly_temp.groupby('decade')['monthly_temperature_C'].mean().reset_index().rename(columns={'monthly_temperature_C':'avg_decade_temp_C'})

# Create a "date" for the middle of the decade to plot the line smoothly
decade_avg['decade_date'] = pd.to_datetime(decade_avg['decade'].astype(str) + "-01-01")



#Plotting a graph that shows the temperatures for each month from 1940 to 2024 in a single time series along with decade averages

fig2 = go.Figure()

#Getting date and temperature to plot the time series
temp = df_monthly_temp['monthly_temperature_C']
years = df_monthly_temp['date']

#Plotting the temperatures from 1940 to 2024
fig2.add_trace(go.Scatter(
    x = years, y = temp,
    mode = 'lines',
    line = dict( width = 1, color = 'black'),
    opacity = 0.9,
    name = 'Temperature',
    hovertemplate=
            '<b>Date:</b> %{x}<br>' +
            '<b>Temperature:</b> %{y:.2f} °C<extra></extra>'
))

#Plotting straight lines for each decade averages

#Setting different colors for each decade average
decade_colors = {1940: "#2d8dd2", 1950: "#2ca02c", 1960: "#9467bd", 1970: "#17becf", 1980:"#5b37ea", 1990:"#9e6155", 2000:"#ecca0a", 2010:"#91fe5f", 2020:'#d62728', }  

#Plotting a straight line for each decade average temperature and making them each a different color
for _, row in decade_avg.iterrows():
    start_year = pd.to_datetime(f"{row['decade']}-01-01") #Start of the decade
    end_year = pd.to_datetime(f"{row['decade']+9}-12-31") #End of the decade
    fig2.add_trace(go.Scatter(
        x = [start_year, end_year],
        y = [row['avg_decade_temp_C']] * 2,
        mode = 'lines',
        line = dict(width = 3, color = decade_colors[row['decade']]),
        name = f"{int(row['decade'])}s avg",
        hovertemplate = 
        f"<b>Decade:</b> {int(row['decade'])}s<br><b>Avg Temperature:</b> {row['avg_decade_temp_C']:.2f} °C<extra></extra>"
    ))

#Overall layout for the graph
fig2.update_layout(
    title = "Temperature of Nepal (1940 to 2024) with Average Temperature for Different Decades",
    title_font = dict(size = 24, family = "Calibri", color = "black", weight  =  'bold'),  
    xaxis = dict(
        title = "Year",
        title_font = dict(size = 22, family = "Calibri", color = "black", weight  =  'bold'),  
        tickfont = dict(size = 18, family = "Calibri", color = "black", weight  =  'bold')
    ),
    yaxis = dict(
        title = "Temperature (°C)",
        title_font = dict(size = 22, family = "Calibri", color = "black", weight  =  'bold'), 
        tickfont = dict(size = 18, family = "Calibri", color = "black", weight  =  'bold')     
    ),
    legend = dict(
        # title = "Legend",
        orientation = "h",
        yanchor = "bottom",
        y = 0.01,
        xanchor = "right",
        x = 0.999,
        # title_font = dict(size = 14, family = "Calibri", color = "black", weight  =  'bold'), 
        font = dict(size = 12, family = "Calibri", color = "black", weight  =  'bold'),       
    bordercolor = "Black",
    borderwidth = 2
    ),
    template = "plotly_white",
    width = 1600, height = 500
)

#Displaying the chart
st.plotly_chart(fig2, use_container_width=True)



#Annual Temeparatures and trend line

#Getting average annual temperatures (in K and C)

print(df_monthly_temp)
df_annual_temp = df_monthly_temp.groupby('year')['monthly_temperature_C'].mean().reset_index()
df_annual_temp.rename(columns={'monthly_temperature_C': 'annual_temperature_C'}, inplace=True)

# print("annual",df_annual_temp)
# df_annual_temp['annual_temperature_C'] = df_annual_temp['annual_temperature_K'] - 273.15

#Getting the x and y variables for regression
temp = df_annual_temp['annual_temperature_C']
years = df_annual_temp['year']

#Using lineear regression to get required values
slope, intercept, r_value, p_value, std_err = linregress(years, temp)

#Getting the trend line using given variables
trend_line = slope * years + intercept


#Plotting a graph that shows the annual temperatures from 1940 to 2024 and trend line 

fig3 = go.Figure()

#Getting date and temperature to plot the time series
temp = df_annual_temp['annual_temperature_C']
years = df_annual_temp['year']

#Plotting the temperatures from 1940 to 2024
fig3.add_trace(go.Scatter(
    x = years, y = temp,
    mode = 'lines+markers',
    line = dict(width = 4, color = 'red'),
    marker=dict(
            color='white',
            size=11,
            line=dict(
                color='red',
                width=2
            )
        ),
    opacity = 0.9,
    name = 'Temperature',
    hovertemplate=
            '<b>Date:</b> %{x}<br>' +
            '<b>Temperature:</b> %{y:.2f} °C<extra></extra>'
))

#Plotting the trend line
fig3.add_trace(go.Scatter(
    x = years, y = trend_line,
    mode = 'lines',
    line = dict(width = 3, color = 'black', dash = 'dash'),
    opacity = 0.7,
    name = 'Trend line',
    hovertemplate=
            '<b>Date:</b> %{x}<br>'
            '<b>Predicted Temperature:</b> %{y:.2f} °C<extra></extra>'
))


#Overall layout for the graph
fig3.update_layout(
    title = "Annual Average Temperature of Nepal (1940 to 2024) with Trend Line",
    title_font = dict(size = 24, family = "Calibri", color = "black", weight  =  'bold'),  
    xaxis = dict(
        title = "Year",
        title_font = dict(size = 22, family = "Calibri", color = "black", weight  =  'bold'),  
        tickfont = dict(size = 18, family = "Calibri", color = "black", weight  =  'bold')
    ),
    yaxis = dict(
        title = "Temperature (°C)",
        title_font = dict(size = 22, family = "Calibri", color = "black", weight  =  'bold'), 
        tickfont = dict(size = 18, family = "Calibri", color = "black", weight  =  'bold')     
    ),
    legend = dict(
        # title = "Legend",
        orientation = "h",
        yanchor = "bottom",
        y = 0.01,
        xanchor = "right",
        x = 0.999,
        title_font = dict(size = 18, family = "Calibri", color = "black", weight  =  'bold'), 
        font = dict(size = 16, family = "Calibri", color = "black", weight  =  'bold'),       
    bordercolor = "Black",
    borderwidth = 2
    ),
    template = "plotly_white",
    width = 1600, height = 600
)

#Text to be added for trend line
trend_line_text = (
    "<b>Trend line variables:</b><br>"
    f"Slope: {slope:.5f} °C/year<br>"
    f"R²: {r_value**2:.3f}<br>"
    f"p-value: {p_value:.3e}<br>"
)

#Adding trend line variables as a box in the figure
fig3.add_annotation(
    xref="paper", yref="paper", 
    x=0.01, y=0.95,             
    text=trend_line_text,
    showarrow=False,
    bordercolor="black",
    borderwidth=1,
    borderpad=5,
    bgcolor="white",
    opacity=0.9,
    font=dict(family="Calibri", size=14, color="black")
)

#Displaying the chart
st.plotly_chart(fig3, use_container_width=True)



