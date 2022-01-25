from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule

from .agents import SsAgent, Sugar, Cop, Criminal
from .model import SugarscapeCg

from matplotlib import cm
from matplotlib.colors import rgb2hex

colors = cm.get_cmap('inferno', 50) # 50 colors out of inferno cmap
hex_codes = []

for i in range(colors.N):
    rgba = colors(i)
    hex_codes.append(rgb2hex(rgba))

#color_dic = { i : hex_codes[i] for i in range(0, len(hex_codes)) }

#color_dic = {4: "#005C00", 3: "#008300", 2: "#00AA00", 1: "#00F800"}
color_dic = {0: "#D5D9DC", 4: "#005C00", 3: "#008300", 2: "#00AA00", 1: "#00F800",29:"#D123F3", 26: "#19F834", 28: "#128720",36:'#0F4C16',49:"#F5F51C",44:"#F5C41C",37:"#F5921C",25:"#F51CE1"}


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
chart_element2 = ChartModule([{"Label": "Criminal Count", "Color": "#AA0000"}])
chart_element3 = ChartModule([{"Label": "Criminal in Jail Count", "Color": "#AA0000"}])
chart_element4 = ChartModule([{"Label": "Crimes commited", "Color": "#AA0000"}])
chart_element5 = ChartModule([{"Label": "Centrum", "Color": "#AA0000"},{"Label": "Noord", "Color": "#0000FF"},{"Label": "West", "Color": "#00FF00"},{"Label": "Nieuw-West", "Color": "#964B00"},{"Label": "Zuid", "Color": "#89CFF0"},{"Label": "Oost", "Color": "#A020F0"},
{"Label": "Zuidoost", "Color": "#FFC0CCB"}])



server = ModularServer(
    SugarscapeCg, [canvas_element, chart_element,chart_element2,chart_element3,chart_element4,chart_element5], "Criminals versus Cops Amsterdam"
)
# server.launch()
