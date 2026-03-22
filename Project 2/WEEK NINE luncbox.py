import phe1123_v3 as phe
import pandas as pd
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import lstsq
import os
import csv
from datetime import datetime
import time

## use lunch box

message = 'ReadSCD'
port = 'COM3'
filename = 'sensor_data.csv'

file_exist = os.path.isfile(filename)

if not file_exist:
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Datetime', 'CO2_ppm', 'Temperature_C', 'Humidity_%'])

try:
    while True:
        response = phe.send_and_receive_message(message, port)
        print(f'Response: {response}')

        parts = response.split(',')

        if len(parts) == 3:
            co2 = int(parts[0])
            temperature = float(parts[1])
            humidity = float(parts[2])

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(filename, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, co2, temperature, humidity])

            print(f"\nSensor Readings at {timestamp}:")
            print(f"CO₂: {co2} ppm")
            print(f"Temperature: {temperature:.2f} °C")
            print(f"Humidity: {humidity:.2f} %")
            print(f"Data saved to: {os.path.abspath(filename)}")
            print("=" * 40)
        else:
            print(f'Error response format: {response}')
        time.sleep(5)
               
except KeyboardInterrupt:
    print('Logging Stopped')

    print("\nFile contents:")
    with open(filename, 'r') as file:
        print(file.read())

df1 = pd.read_csv('sensor_data.csv')


## Adding time column

df1 = phe.add_time_column(df1)

print(df1)

## Create matrix

column1 = df1['Time']
column2 = column1*0 + 1

A = np.column_stack((column1 , column2))
B = df1['CO2_ppm']

## finding solns

x, residuals , rank , s = lstsq(A, B)
slope, intercept = x            ## unpack x
print()
print(x)
print()

print()
print(f'slope : {slope:.0f}')
print(f'intercept : {intercept:.2f}')
print()

## ODE

D = - slope
CO2Ex = df1['CO2_ppm'].iloc[0] ##   need to cfm
##CO2Ex = (intercept - r1)/D
r1 = intercept - (D * CO2Ex)

def ode_fun(t , y):
    CO2 = y[0]
    r2 =  D * (CO2 - CO2Ex)
    dydt = r1 - r2

    return dydt

y0 = [CO2Ex]
t_start = 0 
t_stop = 1

t_span = (t_start , t_stop)
t_eval = np.linspace(t_start , t_stop , 100)

sol=solve_ivp(ode_fun , t_span , y0 , t_eval=t_eval)

t = sol.t
y = sol.y[0]

fig1 = phe.create_figure(
xlabel = "Time (h)",
ylabel = "CO2 (ppm)"
)

trace_ode = phe.line_plot(
x = t,
y = y,
name = "Predicted CO2 (ppm)",
cname = "red"
)

trace_data = phe.marker_plot(
x = df1["Time"],
y = df1["CO2_ppm"],
name = "Data",
cname = "blue"
)

fig1.add_trace(trace_ode)
fig1.add_trace(trace_data)

fig1.show()

print('THIS IS A TEST')