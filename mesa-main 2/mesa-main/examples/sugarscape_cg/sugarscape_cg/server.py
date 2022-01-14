from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule

from .agents import SsAgent, Sugar, Cop
from .model import SugarscapeCg

#color_dic = {4: "#005C00", 3: "#008300", 2: "#00AA00", 1: "#00F800"}
color_dic = {0: "#D5D9DC", 4: "#005C00", 3: "#008300", 2: "#00AA00", 1: "#00F800",28.5: "#D123F3", 26.1: "#19F834", 29.1: "#128720",36.1:'#0F4C16',49:"#F5F51C",44.9:"#F5C41C",37.5:"#F5921C",25.7:"#F51CE1"}


def SsAgent_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is SsAgent:
        portrayal["Shape"] = "sugarscape_cg/resources/ant.png"
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
chart_element = ChartModule([{"Label": "SsAgent", "Color": "#AA0000"}])

server = ModularServer(
    SugarscapeCg, [canvas_element, chart_element], "Sugarscape 2 Constant Growback"
)
# server.launch()
