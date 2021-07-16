from project13 import df

from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool, ColumnDataSource

#convert the datetime datatype to string
df["Start_str"] = df["Start"].dt.strftime("%Y-%m-%d %H:%M:%S")
df["End_str"] = df["End"].dt.strftime("%Y-%m-%d %H:%M:%S")
cds = ColumnDataSource(df)
p = figure(x_axis_type = "datetime", height = 100, width = 500, title = "Motion Graph")
p.yaxis.minor_tick_line_color = None #hide the unnecessary ticks on y-axis
 #hide the intermmediate lines/grid in the graph
#draw the bar chart with the quad glyph
p.yaxis.ticker.desired_num_ticks = 1
hover = HoverTool(tooltips = [("Start", "@Start_str"), ("End", "@End_str")])
p.add_tools(hover)
q = p.quad(left = "Start", right = "End", top=1, bottom=0, color = "green",source = cds)
output_file("template\\"+"Graph.html")
show(p)