"""
Sugarscape Constant Growback Model
================================

Replication of the model found in Netlogo:
Li, J. and Wilensky, U. (2009). NetLogo Sugarscape 2 Constant Growback model.
http://ccl.northwestern.edu/netlogo/models/Sugarscape2ConstantGrowback.
Center for Connected Learning and Computer-Based Modeling,
Northwestern University, Evanston, IL.
"""

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from .agents import SsAgent, Sugar, Cop, Criminal
from .schedule import RandomActivationByBreed

import os
import random

base_path = os.path.dirname(os.path.abspath(__file__))


class SugarscapeCg(Model):
    """
    Sugarscape 2 Constant Growback
    """

    verbose = True  # Print-monitoring

    n_cops = 0  
    cops_that_stepped = 0
    distribution_changes = {'Centrum': 0, 'Nieuw-West': 0, 'Noord': 0, 'Oost': 0, 'West': 0, 'Westpoort': 0, 'Zuid': 0, 'Zuidoost': 0}
    made_changes = {'Centrum': 0, 'Nieuw-West': 0, 'Noord': 0, 'Oost': 0, 'West': 0, 'Westpoort': 0, 'Zuid': 0, 'Zuidoost': 0}
    districts_in_deficit = []
    districts_in_surplus = []

    def __init__(self, height=50, width=50, initial_population_criminals=50,initial_population_cops=100):
        """
        Create a new Constant Growback model with the given parameters.

        Args:
            initial_population: Number of population to start with
        """

        # Set parameters
        self.height = height
        self.width = width
        self.initial_population_criminals = initial_population_criminals
        self.initial_population_cops = initial_population_cops

        self.schedule = RandomActivationByBreed(self)
        self.grid = MultiGrid(self.height, self.width, torus=False)
        self.datacollector = DataCollector(
            {"Criminal Wealth": lambda m: m.schedule.get_breed_count(SsAgent),
            "Criminal Count": lambda m: m.schedule.get_criminal_count(),
            "Criminal in Jail Count": lambda m:m.schedule.get_criminal_count_in_jail() }
        )

        # Create sugar
        import numpy as np
        
        sugar_distribution = np.genfromtxt(base_path + "/amsterdam50x50.txt")
        for _, x, y in self.grid.coord_iter():
            max_sugar = sugar_distribution[x, y]
            sugar = Sugar((x, y), self, max_sugar)
            self.grid.place_agent(sugar, (x, y))
            self.schedule.add(sugar)

        # # Create agent:
        # for i in range(self.initial_population_criminals):
        #     x = self.random.randrange(self.width)
        #     y = self.random.randrange(self.height)
        #     sugar = self.random.randrange(6, 25)
        #     metabolism = self.random.randrange(2, 4)
        #     vision = self.random.randrange(1, 6)
        #     ssa = SsAgent((x, y), self, False, sugar, metabolism, vision)
        #     self.grid.place_agent(ssa, (x, y))
        #     self.schedule.add(ssa)

        # Create agent:
        for i in range(self.initial_population_criminals):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            wealth = self.random.randrange(6, 25)
            risk_tolerance = random.random()
            search_radius = self.random.randrange(1, 3)
            criminal = Criminal((x, y), self, True, wealth, risk_tolerance, search_radius)
            self.grid.place_agent(criminal, (x, y))
            self.schedule.add(criminal)
        
        for i in range(self.initial_population_cops):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            #id = i = self.random.randrange(6, 25)
            cop = Cop((x, y) ,self)
            self.grid.place_agent(cop, (x, y))
            self.schedule.add(cop)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)
        if self.verbose:
            print([self.schedule.time, self.schedule.get_breed_count(SsAgent)])

    def run_model(self, step_count=200):

        if self.verbose:
            print(
                "Initial number Sugarscape Agent: ",
                self.schedule.get_breed_count(SsAgent),
            )

        for i in range(step_count):
            self.step()

        if self.verbose:
            print("")
            print(
                "Final number Sugarscape Agent: ",
                self.schedule.get_breed_count(SsAgent),
            )
