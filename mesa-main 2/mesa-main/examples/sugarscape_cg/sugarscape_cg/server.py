from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule

from .agents import Sugar, Cop, Criminal
from .model import SugarscapeCg

from matplotlib import cm
from matplotlib.colors import rgb2hex, ListedColormap

# colors = cm.get_cmap('inferno', 50) # 50 colors out of inferno cmap

# district_names = ['Centrum', 'Noord', 'West', 'Zuid', 'Zuidoost', 'Oost', 'Nieuw-West']
color_dic = {44: '#eb534b', 28: '#34b7eb', 36: '#40943d', 49: '#ebc934', 25: '#800080', 37: '#50d950', 29: '#ffc0cb'}
# colors = ListedColormap(district_colors)

# hex_codes = []

# for i in range(colors.N):
#     rgba = colors(i)
#     hex_codes.append(rgb2hex(rgba))

# color_dic = { i : hex_codes[i] for i in range(0, len(hex_codes)) }

# print(color_dic)

#color_dic = {4: "#005C00", 3: "#008300", 2: "#00AA00", 1: "#00F800"}
# color_dic = {0: "#D5D9DC", 4: "#005C00", 3: "#008300", 2: "#00AA00", 1: "#00F800",29:"#D123F3", 26: "#19F834", 28: "#128720",36:'#0F4C16',49:"#F5F51C",44:"#F5C41C",37:"#F5921C",25:"#F51CE1"}


def SsAgent_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is Criminal:
        portrayal["Shape"] = "sugarscape_cg/resources/criminal.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1
    
    elif type(agent) is Cop:
        portrayal["Shape"] = "sugarscape_cg/resources/cop.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1
    

    elif type(agent) is Sugar:
        if agent.amount != 0:
            portrayal["Color"] = color_dic.get(agent.amount, "#D5D9DC")
        else:
            portrayal["Color"] = "#D6F5D6"
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1
    

    return portrayal


canvas_element = CanvasGrid(SsAgent_portrayal, 50, 50, 500, 500)
chart_element = ChartModule([{"Label": "Criminal Wealth", "Color": "#AA0000"}])
chart_element3 = ChartModule([{"Label": "Criminal in Jail Count", "Color": "#AA0000"}])
chart_element4 = ChartModule([{"Label": "Crimes commited", "Color": "#AA0000"}])
chart_element5 = ChartModule([{"Label": "Centrum", "Color": "#eb534b"},{"Label": "Noord", "Color": "#34b7eb"},{"Label": "West", "Color": "#40943d"},{"Label": "Nieuw-West", "Color": "#ffc0cb"},{"Label": "Zuid", "Color": "#ebc934"},{"Label": "Oost", "Color": "#50d950"},
{"Label": "Zuidoost", "Color": "#800080"}])
chart_element6 = ChartModule([{"Label": "Centrum_Avg", "Color": "#eb534b"},{"Label": "Noord_Avg", "Color": "#34b7eb"},{"Label": "West_Avg", "Color": "#40943d"},{"Label": "Nieuw-West_Avg", "Color": "#ffc0cb"},{"Label": "Zuid_Avg", "Color": "#ebc934"},{"Label": "Oost_Avg", "Color": "#50d950"},
{"Label": "Zuidoost_Avg", "Color": "#800080"}])



server = ModularServer(
    SugarscapeCg, [canvas_element, chart_element,chart_element3,chart_element4,chart_element5,chart_element6], "Criminals versus Cops Amsterdam"
)
# server.launch()
