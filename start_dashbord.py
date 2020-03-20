import pandas as pd
import numpy as np
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import ClientsideFunction, Input, Output, State
import plotly.figure_factory as ff

init_table = pd.read_csv("plot_hefte_.csv",sep="\t")
init_table = init_table.drop(init_table[init_table["genre"] == "?"].index)
init_table = init_table.drop(init_table[init_table["title"] == "?"].index)
init_table = init_table.drop(init_table[init_table["end"] == "?"].index)
init_table = init_table.drop(init_table[init_table["start"] == "?"].index)
init_table = init_table.drop(init_table[init_table["publisher"] == "?"].index)
init_table = init_table.drop(init_table[init_table["count"] == "?"].index)

init_table["end"] = init_table["end"].astype(int)
init_table["start"] = init_table["start"].astype(int)
init_table["count"] = init_table["count"].astype(int)

app = dash.Dash(__name__)
app.title = "Heftroman Universum"

app.layout = html.Div(children=[html.H1(children="Heftroman Universum"),
				html.Table(children=[
					html.Tr(children=[html.Td(dcc.Graph(id="gantt", style={"width": "100vw"}))]),
					html.Tr(children=[html.Td(dcc.Graph(id="stackplot", style={"width": "100vw"}))])
						    ]),
				dash_table.DataTable(
		id='table',
		editable=False,
		columns=[{"name": i, "id": i} for i in init_table.columns],
		data=init_table.to_dict('rows'),
		style_cell={'width': '50px'},
		sort_action="native",
		row_selectable='single',
		filter_action='native',
		selected_rows=[],
		style_table={
			'maxHeight': '50hv',
			'overflowY': 'scroll',
			'maxWidth': '70wv'
		}

	)
			
])

def calc_year(x):
    
    duration = int(x["end"])-int(x["start"])+1
    try:
    	perY = int(x["count"])/duration
    except:
        print(x)
    return perY

def get_per_year_ratio(data):

	data["peryear"] = data.apply(lambda x: calc_year(x), axis=1)
	years = range(min(data["start"].astype(int)),max(data["end"].astype(int)),1)
	all_output = []
	fantasy_output = []
	rom_output = []
	hor_output = []
	wes_output = []
	krieg_output = []
	aben_output = []
	scifi_output = []
	krimi_output = []
	liebe_output = []
	for year in years:
	    
	    all_output.append(data[(data["end"] >= year) & (data["start"] <= year)]["peryear"].sum())
	    fantasy_output.append(data[(data["end"] >= year) & (data["start"] <= year) & (data["genre"] == "Fantasy")]["peryear"].sum())
	    rom_output.append(data[(data["end"] >= year) & (data["start"] <= year) & (data["genre"] == "romatic suspense")]["peryear"].sum())
	    hor_output.append(data[(data["end"] >= year) & (data["start"] <= year) & (data["genre"] == "Horror")]["peryear"].sum())
	    krieg_output.append(data[(data["end"] >= year) & (data["start"] <= year) & (data["genre"] == "Krieg")]["peryear"].sum())
	    aben_output.append(data[(data["end"] >= year) & (data["start"] <= year) & (data["genre"] == "Abenteuer")]["peryear"].sum())
	    wes_output.append(data[(data["end"] >= year) & (data["start"] <= year) & (data["genre"] == "Western")]["peryear"].sum())
	    scifi_output.append(data[(data["end"] >= year) & (data["start"] <= year) & (data["genre"] == "SciFi")]["peryear"].sum())
	    krimi_output.append(data[(data["end"] >= year) & (data["start"] <= year) & (data["genre"] == "Krimi")]["peryear"].sum())
	    liebe_output.append(data[(data["end"] >= year) & (data["start"] <= year) & (data["genre"] == "Liebe")]["peryear"].sum())
	year_plot = pd.DataFrame()

	year_plot["year"] = years
	year_plot["Hefte"] = all_output
	year_plot["Fantasy"] = fantasy_output
	year_plot["Rom"] = rom_output
	year_plot["Horror"] = hor_output
	year_plot["Western"] = wes_output
	year_plot["Krieg"] = krieg_output
	year_plot["Abenteuer"] = aben_output
	year_plot["SciFi"] = krieg_output
	year_plot["Krimi"] = aben_output
	year_plot["Liebe"] = liebe_output

	return year_plot

@app.callback(Output('gantt', 'figure'),
	     [Input('table', 'derived_virtual_data'),
	      Input("table","data")])
def gantt_plot(input_data, nochange_table):

	if input_data is None:
		input_data = nochange_table
	input_data = pd.DataFrame(input_data)
	input_data = input_data.sort_values("start")
	df = []
	colors = []
	col_dict = {"Fantasy":"#009900","romatic suspense":"#993399","Horror":"#000000","Krieg":"#8f8c85","Western":"#b59345","Abenteuer":"#b54550","Krimi":"#fff200","SciFi":"#8f0191","Liebe":"#ff0000"}
	for index, row in input_data.iterrows():
	    	df.append(dict(Task=row["title"],Start=row["start"],Finish=row["end"],Resource=row["publisher"]))
	    	colors.append(col_dict[row["genre"]])
	
	fig = ff.create_gantt(df, colors=colors, height=600)

	return fig

@app.callback(Output('stackplot', 'figure'),
	     [Input('table', 'derived_virtual_data'),
	      Input("table","data")])
def stack_plot(input_data, nochange_table):

	if input_data is None:
		input_data = nochange_table
	input_data = pd.DataFrame(input_data)
	input_data = input_data.sort_values("start")
	year_plot = get_per_year_ratio(input_data)
	stack_frame = pd.DataFrame()
	stack_frame["Year"] = list(year_plot["year"])*9
	stack_frame["Genre"] = len(year_plot)*["Fantasy"]+len(year_plot)*["Rom. Sus."]+len(year_plot)*["Horror"]+len(year_plot)*["Western"]+len(year_plot)*["Krieg"]+len(year_plot)*["Abenteuer"]+len(year_plot)*["SciFi"]+len(year_plot)*["Krimi"]+len(year_plot)*["Liebe"]
	stack_frame["Hefte"] = list(year_plot["Fantasy"])+list(year_plot["Rom"])+list(year_plot["Horror"])+list(year_plot["Western"])+list(year_plot["Krieg"])+list(year_plot["Abenteuer"])+list(year_plot["SciFi"])+list(year_plot["Krimi"])+list(year_plot["Liebe"])

	stack_fig = px.area(stack_frame, x="Year", y="Hefte", color="Genre", line_group="Genre")
	return stack_fig


if __name__ == '__main__':
    app.run_server(debug=True)
