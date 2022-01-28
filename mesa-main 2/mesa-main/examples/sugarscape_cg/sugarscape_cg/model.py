"""
Sugarscape Constant Growback Model
================================

Replication of the model found in Netlogo:
Li, J. and Wilensky, U. (2009). NetLogo Sugarscape 2 Constant Growback model.
http://ccl.northwestern.edu/netlogo/models/Sugarscape2ConstantGrowback.
Center for Connected Learning and Computer-Based Modeling,
Northwestern University, Evanston, IL.
"""

from itertools import count
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from sqlalchemy import true

from .agents import Sugar, Cop, Criminal
from .schedule import RandomActivationByBreed

import os
import random
import numpy as np

base_path = os.path.dirname(os.path.abspath(__file__))


class SugarscapeCg(Model):
    """
    Sugarscape 2 Constant Growback
    """

    verbose = False  # Print-monitoring

    n_cops = 0  
    cops_that_stepped = 0
    distribution_changes = {'Centrum': 0, 'Nieuw-West': 0, 'Noord': 0, 'Oost': 0, 'West': 0, 'Zuid': 0, 'Zuidoost': 0, 'Undefined':0}
    made_changes = {'Centrum': 0, 'Nieuw-West': 0, 'Noord': 0, 'Oost': 0, 'West': 0, 'Zuid': 0, 'Zuidoost': 0, 'Undefined':0}
    surveillance_levels ={'Centrum': 8, 'Nieuw-West': 2, 'Noord': 6, 'Oost': 6, 'West': 6, 'Zuid': 6, 'Zuidoost': 6, 'Undefined':0}
    # surveillance_levels ={'Centrum': 3, 'Nieuw-West': 1, 'Noord': 2, 'Oost': 2, 'West': 2, 'Westpoort': 1, 'Zuid': 2, 'Zuidoost': 2, 'Undefined':0}
    districts_in_deficit = []
    districts_in_surplus = []

    def __init__(self, height=50, width=50, initial_population_criminals=45, initial_population_cops=40, criminal_risk_radius=5, cop_catch_radius=1, jail_sentence=10, criminal_risk_aversion=100, criminal_disconnectivity=45):
        """
        Create a new Constant Growback model with the given parameters.

        Args:
            initial_population: Number of population to start with
        """

        # Set parameters
        self.height = height
        self.width = width
        self.initial_wealth_distribution = np.genfromtxt(base_path + "/amsterdam50x50new.txt")

        self.initial_population_criminals = initial_population_criminals
        self.initial_population_cops = initial_population_cops

        self.criminal_risk_radius = criminal_risk_radius
        self.criminal_risk_aversion = criminal_risk_aversion
        self.criminal_disconnectivity = criminal_disconnectivity

        self.cop_catch_radius = cop_catch_radius
        self.jail_sentence = jail_sentence

        self.schedule = RandomActivationByBreed(self)
        self.grid = MultiGrid(self.height, self.width, torus=False)
        self.datacollector = DataCollector(
            {"Criminal Wealth": lambda m: m.schedule.get_breed_count(),
            "Criminal Count": lambda m: m.schedule.get_criminal_count(),
            "Criminal in Jail Count": lambda m:m.schedule.get_criminal_count_in_jail(),
            "Crimes commited": lambda m:m.schedule.get_crimes_commited(),
            "Centrum": lambda m:m.schedule.get_crimes_per_timestep().get("Centrum"),
            "Noord": lambda m:m.schedule.get_crimes_per_timestep().get("Noord"),
            "West": lambda m:m.schedule.get_crimes_per_timestep().get("West"),
            "Zuid": lambda m:m.schedule.get_crimes_per_timestep().get("Zuid"),
            "Zuidoost": lambda m:m.schedule.get_crimes_per_timestep().get("Zuidoost"),
            "Oost": lambda m:m.schedule.get_crimes_per_timestep().get("Oost"),
            "Nieuw-West": lambda m:m.schedule.get_crimes_per_timestep().get("Nieuw-West")}
        )

        # Create sugar
        sugar_distribution = np.genfromtxt(base_path + "/amsterdam50x50new.txt")
        for _, x, y in self.grid.coord_iter():
            max_sugar = sugar_distribution[x, y]
            sugar = Sugar((x, y), self, max_sugar)
            self.grid.place_agent(sugar, (x, y))
            self.schedule.add(sugar)

        # Create agent:
        for i in range(self.initial_population_criminals):
            while(True):
                x = self.random.randrange(self.width)
                y = self.random.randrange(self.height)
                if(self.get_district((x,y)) != "Undefined"):
                    break
            wealth = self.random.randrange(6, 25)
            risk_aversion = self.random.randrange(0, self.criminal_risk_aversion)

            criminal = Criminal((x, y), self, buddy_id=random.randint(0, self.criminal_disconnectivity), moore=True, wealth=wealth, risk_aversion=risk_aversion, risk_radius=self.criminal_risk_radius)
            self.grid.place_agent(criminal, (x, y))
            self.schedule.add(criminal)
        
        for i in range(self.initial_population_cops):
            while(True):
                x = self.random.randrange(self.width)
                y = self.random.randrange(self.height)
                if(self.get_district((x,y)) != "Undefined"):
                    break
            #id = i = self.random.randrange(6, 25)
            cop = Cop((x, y), self, catch_radius=self.cop_catch_radius, jail_sentence=self.jail_sentence)
            self.grid.place_agent(cop, (x, y))
            self.schedule.add(cop)
            self.n_cops +=1

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)
        if self.verbose:
            print([self.schedule.time, self.schedule.get_breed_count()])

    def run_model(self, step_count=200):

        if self.verbose:
            print(
                "Initial number Sugarscape Agent: ",
                self.schedule.get_breed_count(),
            )

        for i in range(step_count):
            self.step()

        if self.verbose:
            print("")
            print(
                "Final number Sugarscape Agent: ",
                self.schedule.get_breed_count(),
            )

    def get_district(self, pos):
        """Get respective district of an input position.
 
        :param pos: position
        :type pos: tuple of ints (x, y)
        
        :rtype: string
        :return: district name
        """
        x = pos[0]
        y = pos[1]

        initial_wealth = self.initial_wealth_distribution[x][y]

        if initial_wealth == 28.0:
            return 'Noord'
        elif initial_wealth == 29.0:
            return 'Nieuw-West'
        elif initial_wealth == 36.0:
            return 'West'
        elif initial_wealth == 44.0:
            return 'Centrum'
        elif initial_wealth == 37.0:
            return 'Oost'
        elif initial_wealth == 49.0:
            return 'Zuid'
        elif initial_wealth == 25.0:
            return 'Zuidoost'
        else:
            return 'Undefined'

    def get_agents_per_district(self, agent_type):
        """Get count of agents per district.
 
        :param agent_type: Cop or Criminal to be counted
        :type agent_type: class
        
        :rtype: dict
        :return: dictionary with district names as keys and respective counts of agent_type
        """
        districts_dict = {}
        
        for agents, x, y in self.grid.coord_iter():
            district = self.get_district((x, y))
            if district not in districts_dict.keys():
                districts_dict[district] = 0
            for agent in agents:
                if type(agent) is agent_type:
                    districts_dict[district] += 1

        return districts_dict

    def get_crimes_per_district(self):
        """Get count of agents per district.
 
        :param agent_type: Cop or Criminal to be counted
        :type agent_type: class
        
        :rtype: dict
        :return: dictionary with district names as keys and respective counts of agent_type
        """
        districts_crimes_dict = {}
        
        for agents, x, y in self.grid.coord_iter():
            district = self.get_district((x, y))
            if district not in districts_crimes_dict.keys():
                districts_crimes_dict[district] = 0
            for agent in agents:
                if type(agent) is Criminal:
                    if agent.does_crime:
                        districts_crimes_dict[district] += 1   
                    #districts_crimes_dict[district] += agent.crimes_commited

        return districts_crimes_dict