## Version
# Created on Feb. 28, 2025
#         by Zhou Kang

## Import modules
import serial.tools.list_ports
import time
import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio
import numpy as np
from bs4 import BeautifulSoup

## Define functions

# a simple function to plot xdata and ydata using
# marker plot
def plot_xy(
    x, # xdata
    y, # ydata
    xlabel = "", # label of x axis
    ylabel = "", # label of y axis
    name = "", # label of the trace
    cname = "blue" # color the trace
):
    fig1 = create_figure(
        xlabel = xlabel,
        ylabel = ylabel
    )
    trace1 = marker_plot(
        x = x,
        y = y,
        name = name,
        cname = cname
    )
    fig1.add_trace(trace1)
    fig1.show()

# This functions adds a column named as "Time" to a df. It requires
# the df has a column named as "Datetime".
def add_time_column(df1):
    datetime0_str = df1.at[0,'Datetime']
    for ri in range(len(df1)):
        datetime1_str = df1.at[ri,'Datetime']
        datetime0 = pd.to_datetime(datetime0_str)
        datetime1 = pd.to_datetime(datetime1_str)
        delta_dt = datetime1 - datetime0
        time1 = delta_dt.total_seconds()/3600
        df1.at[ri,'Time'] = time1
    return(df1)

# This function slice a df by using two time points (start and stop).
# It requires df has a column named as "Time". It will keep the rows
# whose values of "Time" column are within the start and stop points.
def slice_df(
    df1, # the input dataframe
    start, # the start point for slicing
    stop # the stop point for slicing
    ):
    df1 = add_time_column(df1)
    condition1 = df1["Time"] > start
    condition2 = df1["Time"] < stop
    df1 = df1.loc[condition1 & condition2]
    df1 = df1.reset_index()
    return df1

# This function calculates R squared for a solved Ax = b
def calculate_R2(A,b,x):
    e = b - A @ x
    q = b - np.mean(b)
    enorm = e.T @ e
    qnorm = q.T @ q
    R2 = 1 - enorm / qnorm    
    return R2

# This function produces a plot in a html file. The data
# must be stored in a csv file, which must have a column
# named as "Datetime". The data in "Datetime" column will 
# be processed to provide x data. Another column will
# provide ydata
def plot_csv_one_sensor(
    csv_fn, # csv filename
    column_name, # the name of the column providing ydata
    xlabel = "Time (h)", # label of x axis
    ylabel = "", # label of y axis
    auto_open_flag = False # the flag decides if the html 
                           # file will be opened in the script
    ):
    
    fig1 = create_figure(xlabel,ylabel)
    
    df1 = pd.read_csv(csv_fn)
    df1 = add_time_column(df1)
    
    x = df1['Time']
    y = df1[column_name]
    name = ''
    cname = 'blue'
    trace1 = marker_plot(x,y,name,cname)
    
    fig1.add_trace(trace1)
    
    html_fn = csv_fn[:-4] + '.html'
    pio.write_html(fig1, html_fn, 
                   auto_open=auto_open_flag)    
    insert_auto_refresh_script(html_fn)

# This function produces a plot by using two columns in a df. The
# plot is saved in a html file.
def plot_df_two_columns(
    df, # dataframe
    xname, # the name of the column in df providing xdata
    yname, # the name of the column in df providing ydata
    fn # the html filename without extension
    ):
    
    x = df[xname]
    y = df[yname]
    name = ' '
    cname = 'blue'
    
    fig1 = create_figure(xname,yname)
    trace1 = marker_plot(x,y,name,cname)
    
    fig1.add_trace(trace1)
    
    html_fn = fn + '.html'
    pio.write_html(fig1, html_fn, 
                   auto_open=True)

# This function inserts a Javascript to a html file so that the file
# is automatically refeshed every 5 seconds
def insert_auto_refresh_script(html_filename):
    
    with open(html_filename, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    
    refresh_script = soup.new_tag("script")
    refresh_script.string = """
    // Refresh the page every 5 seconds
    setTimeout(() => {
        location.reload();
    }, 5000);
    """
    
    if soup.head:
        soup.head.append(refresh_script)
    else:
        soup.body.append(refresh_script)
    
    with open(html_filename, "w", encoding="utf-8") as file:
        file.write(str(soup))

# This function sends a message to a USB device through a given port.
# It will also listen and report any received response.
def send_and_receive_message(
    message, # a string
    port # name of the USB port connected to FCB box
    ):
    
    # set data transmission speed
    baud_rate = 115200 
    
    # connect to the USB device (FCB box)
    # an object will be created to handle this connection
    # timeout = 5 means that the algorithm will wait for up to 5
    # seconds if there is no response from the USB device
    ser = serial.Serial(port, baud_rate, timeout=5)
    
    # wait 1 second for the device to get ready
    time.sleep(1)
    
    # /n is newline, a character used to make end of a line.
    # we don't type it in our normal words; it is added here
    message += '\n'
    
    # send the message to the USB device
    # "encode" is a method of "message"
    # message.encode() provides the message in byte formate
    # byte is composed of 1 and 0
    ser.write(message.encode())
    
    # read response from the USB device
    # ser is the object we created for the USB (Serial) device
    # readline() provides the received response in byte format
    # decode() converts byte data into string data
    # strip() removes \n and space at two ends of the response
    # after this sequential processing, you get a clean line
    response = ser.readline().decode().strip()
    
    # disconnect the USB device
    ser.close()
    
    # the response is what this function produces
    return response

# This function lists all the USB ports available on the computer
def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    print()
    for port in ports:
        print(port.device)
    print()

# This function creates a blank plotly figure object without a 
# secondary y axis.
def create_figure(
    xlabel, # label of x axis
    ylabel # label of y axis
    ):
    fig = go.Figure()
    fig.update_layout(
        plot_bgcolor = "White",
        xaxis = {
            "ticks": "outside",
            "linecolor": grey,
            "title": xlabel
        },
        yaxis = {
            "ticks": "outside",
            "linecolor": grey,
            "title": ylabel
        },
    )
    return fig

# This function creates a blank plotly figure object with a 
# secondary y axis.
def create_figure_y2(
    xlabel, # label of x axis
    ylabel, # label of primary y axis
    y2label, # label of secondary y axis
    y2cname, # color of seoncdary y axis
    ):
    fig = go.Figure()
    fig.update_layout(
        plot_bgcolor = "White",
        xaxis = {
            "ticks": "outside",
            "linecolor": grey,
            "title": xlabel
        },
        yaxis = {
            "ticks": "outside",
            "linecolor": grey,
            "title": ylabel
        },
        yaxis2 = {
            "ticks": "outside",
            "linecolor": colors[y2cname],
            "tickfont": {"color": colors[y2cname]},
            "title": {
                "text": y2label,
                "font": {
                    "color": colors[y2cname]
                    },
                },
            "overlaying":  "y",
            "side": "right"
        },
        legend = {
            "orientation": "h",
            "xanchor": "center",
            "yanchor": "bottom",
            "y": -0.2,"x": 0.5
        })
    return fig
    

# This function creates a marker trace for plotly fig
def marker_plot(
    x, # data for x axis
    y, # data for y axis
    name, # name of this trace
    cname, # color of this trace
    yaxis = "y" # use primary or secondary y axis
    ):
    color1 = colors[cname]
    trace = go.Scatter(
        x = x, y = y,
        name = name,
        mode = "markers",
        marker = {
            "color": color1
        },         
        yaxis = yaxis
    )
    return trace

# This function creates a line trace for plotly fig
def line_plot(
    x, # data for x axis
    y, # data for y axis
    name, # name of this trace
    cname, # color of this trace
    yaxis = "y" # primary or secondary y axis
    ):
    color1 = colors[cname]
    trace = go.Scatter(
        x = x, y = y,
        name = name,
        mode = "lines",
        marker = {
            "color": color1
        },         
        yaxis = yaxis         
    )
    return trace

# This function prints message with empty lines for ease of reading
def print_with_space(text1):
    print()
    print(text1)
    print()

## Define variables

# Define a few variables to encode colors
blue = "#568EAF"
grey = "#4D4D4D"
brown = "#A08D7C"
red = "#C85945"
green = "#4D9481"
purple = "#AF82A6"
lightgrey = "#808080"

# The type of this variable is dictionary. It allows you to access a 
# value of a field by using the field name. 
colors = {
    "blue": "#568EAF",
    "grey": "#4D4D4D",
    "brown": "#A08D7C",
    "red" : "#C85945",
    "green": "#4D9481",
    "purple": "#AF82A6",
    "lightgrey": "#808080" 
}