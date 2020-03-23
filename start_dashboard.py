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

print(init_table["count"].sum())

app = dash.Dash(__name__)
app.title = "Heftroman Universum"

app.layout = html.Div(children=[html.H1(children="Heftroman Universum"),
				html.Table(children=[
					html.Tr(children=[html.Td(dcc.Graph(id="gantt", style={"width": "100vw"}))]),
					html.Tr(children=[html.Td(dcc.Graph(id="pubplot", style={"width": "100vw"}))]),
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

def get_pub_output(data):

	data["peryear"] = data.apply(lambda x: calc_year(x), axis=1)
	years = list(range(min(data["start"]),max(data["end"]),1))
	output = []
	pubs = []
	unique_publisher = set(data["publisher"])
	for pub in unique_publisher:
	    
	    select = data[data["publisher"] == pub]
	    
	    for year in years:
	        output.append(select[(select["end"] >= year) & (select["start"] <= year)]["peryear"].sum())
		
	    pubs = pubs + [pub] * len(years)

	pub_output = pd.DataFrame()
	pub_output["Publisher"] = pubs
	pub_output["Hefte"] = output
	pub_output["Year"] = years * len(set(data["publisher"]))

	return pub_output

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
	jugend_output = []
	erotik_output = []
	unklar_output = []
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
	    erotik_output.append(data[(data["end"] >= year) & (data["start"] <= year) & (data["genre"] == "Erotik")]["peryear"].sum())
	    jugend_output.append(data[(data["end"] >= year) & (data["start"] <= year) & (data["genre"] == "Jugend")]["peryear"].sum())
	    unklar_output.append(data[(data["end"] >= year) & (data["start"] <= year) & (data["genre"] == "unklar")]["peryear"].sum())
	year_plot = pd.DataFrame()

	year_plot["year"] = years
	year_plot["Hefte"] = all_output
	year_plot["Fantasy"] = fantasy_output
	year_plot["Rom Sus."] = rom_output
	year_plot["Horror"] = hor_output
	year_plot["Western"] = wes_output
	year_plot["Krieg"] = krieg_output
	year_plot["Abenteuer"] = aben_output
	year_plot["SciFi"] = scifi_output
	year_plot["Krimi"] = krimi_output
	year_plot["Liebe"] = liebe_output
	year_plot["Erotik"] = erotik_output
	year_plot["Jugend"] = jugend_output
	year_plot["Unklar"] = unklar_output

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
	col_dict = {"Fantasy":"#009900","romatic suspense":"#993399","Horror":"#000000","Krieg":"#8f8c85","Western":"#b59345","Abenteuer":"#b54550","Krimi":"#fff200","SciFi":"#8f0191","Liebe":"#ff0000","Erotik":"#f285d0","Jugend":"#4ebfa7","unklar":"#979999"}
	for index, row in input_data.iterrows():
	    	df.append(dict(Task=row["title"],Start=row["start"],Finish=row["end"], Resource=row["genre"],Description=row["title"]+", "+row["publisher"]+", "+str(row["count"])+" Hefte"))
	    	colors.append(col_dict[row["genre"]])
	
	fig = ff.create_gantt(df, colors=colors, height=600, index_col='Resource')
	fig["layout"].update(title={"text":"Serien und Publikationszeiträume nach Genres"})
	fig['layout'].update(legend={'x': 1, 'y': 1})
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

	x = list(year_plot.year)
	stack_fig = go.Figure(go.Bar(x=x, y=[0]*len(x), name=''))
	genres= ["Abenteuer","Krimi","Krieg","Western","SciFi","Horror","Fantasy","Liebe","Rom Sus.","Erotik","Jugend","Unklar"]
	for gen in genres:
    		stack_fig.add_trace(go.Bar(x=x, y=year_plot[gen], name=gen))
    
	stack_fig.update_layout(barmode='stack', xaxis={'categoryorder':'category ascending'})
	stack_fig["layout"].update(title={"text":"Veröffentlichte Romane nach Genre"})
	stack_fig['layout'].update(legend={'x': 1, 'y': 1})
	return stack_fig

@app.callback(Output('pubplot', 'figure'),
	     [Input('table', 'derived_virtual_data'),
	      Input("table","data")])
def pub_plot(input_data, nochange_table):

	if input_data is None:
		input_data = nochange_table
	input_data = pd.DataFrame(input_data)
	input_data = input_data.sort_values("start")

	pub_output = get_pub_output(input_data)

	x = list(pub_output.Year)
	fig = go.Figure(go.Bar(x=x, y=[0]*len(x), name=''))

	for pubs in set(pub_output.Publisher):
	    fig.add_trace(go.Bar(x=x, y=pub_output[pub_output.Publisher == pubs].Hefte, name=pubs))
	    
	fig.update_layout(barmode='stack', xaxis={'categoryorder':'category ascending'})
	fig["layout"].update(title={"text":"Veröffentlichungen über Zeit und Verlage"})
	fig['layout'].update(legend={'x': 1, 'y': 1})
	return fig


if __name__ == '__main__':
    app.run_server(debug=True)
