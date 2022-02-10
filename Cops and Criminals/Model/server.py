from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule

from agents import Sugar, Cop, Criminal
from model import SugarscapeCg

from matplotlib import cm
from matplotlib.colors import rgb2hex, ListedColormap

# colors of the grid
color_dic = {
    44: '#eb534b', 
    28: '#34b7eb', 
    36: '#40943d', 
    49: '#ebc934', 
    25: '#800080', 
    37: '#50d950', 
    29: '#ffc0cb'
}

def SsAgent_portrayal(agent):
    """
    Function that handles the display of the cops and criminals.
    """
    if agent is None:
        return

    portrayal = {}

    # display the criminals
    if type(agent) is Criminal:
        portrayal["Shape"] = "resources/criminal.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1
    
    # display the cops
    elif type(agent) is Cop:
        portrayal["Shape"] = "resources/cop.png"
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

# Specify the canvas elements
canvas_element = CanvasGrid(SsAgent_portrayal, 50, 50, 500, 500)
chart_element = ChartModule(
    [{"Label": "Criminal Wealth", "Color": "#AA0000"}]
)
chart_element3 = ChartModule(
    [{"Label": "Criminal in Jail Count", "Color": "#AA0000"}]
)
chart_element4 = ChartModule(
    [{"Label": "Crimes commited", "Color": "#AA0000"}]
)
chart_element5 = ChartModule(
    [
        {"Label": "Centrum", "Color": "#eb534b"},
        {"Label": "Noord", "Color": "#34b7eb"},
        {"Label": "West", "Color": "#40943d"},
        {"Label": "Nieuw-West", "Color": "#ffc0cb"},
        {"Label": "Zuid", "Color": "#ebc934"},
        {"Label": "Oost", "Color": "#50d950"},
        {"Label": "Zuidoost", "Color": "#800080"}
    ]
)
chart_element6 = ChartModule(
    [
        {"Label": "Centrum_Avg", "Color": "#eb534b"},
        {"Label": "Noord_Avg", "Color": "#34b7eb"},
        {"Label": "West_Avg", "Color": "#40943d"},
        {"Label": "Nieuw-West_Avg", "Color": "#ffc0cb"},
        {"Label": "Zuid_Avg", "Color": "#ebc934"},
        {"Label": "Oost_Avg", "Color": "#50d950"},
        {"Label": "Zuidoost_Avg", "Color": "#800080"}
    ]
)

# Create the server
server = ModularServer(
    SugarscapeCg, 
    [
        canvas_element, 
        chart_element,
        chart_element3,
        chart_element4,
        chart_element5,
        chart_element6
    ], 
    "Criminals versus Cops Amsterdam"
)
