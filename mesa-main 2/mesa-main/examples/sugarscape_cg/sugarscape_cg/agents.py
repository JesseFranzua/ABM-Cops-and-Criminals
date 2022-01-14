import math
import numpy as np
from mesa import Agent
import random


def get_distance(pos_1, pos_2):
    """Get the distance between two point

    Args:
        pos_1, pos_2: Coordinate tuples for both points.

    """
    x1, y1 = pos_1
    x2, y2 = pos_2
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx ** 2 + dy ** 2)

class Criminal(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)

        self.pos = pos
        self.wealth = 100
        self.risk_tolerance = 0.5
        self.search_radius = 1
        self.jail_time = 0
    
    def get_sugar(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is Sugar:
                return agent
                
    def get_wealth(self, pos):
        """
        Returns the wealth in a given cell
        """
        sugar_patch = self.get_sugar(self.pos)
        return 1
    
    def get_risk(self, pos):
        """
        Returns the risk in a given cell
        """
        return 0.4
    
    def do_crime(self, pos):
        """
        Depletes the cell's resources and add them to the criminal's wealth
        """
        loot = self.get_wealth(pos)
        self.wealth += loot
        # do something that erases the cell's wealth
        return loot
    
    def get_caught(self):
        """ 
        Gives the criminal a fine and sends them to jail
        """
        self.wealth -= self.model.fine
        self.jail_time = 5

    def step(self):
        '''
        The criminal makes an inventory of locations available to them,
        decides on where to go,
        moves to that location,
        and tries to do the crime.
        '''
        if self.jail_time > 0:
            self.jail_time -= 1
            return
        
        # get all surrounding cells, can extend to cells of other criminals in the network
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=True, radius=self.search_radius)

        # filter the cells that have an acceptable risk 
        options = [cell for cell in neighborhood if self.get_risk(cell) < self.risk_tolerance]

        # determine which cell has the most wealth
        wealth = [self.get_wealth(cell) for cell in options]
        target_cell = options[np.argmax(wealth)]

        # move the criminal to the target cell
        self.model.grid.move_agent(self, target_cell)

        # do the crime or get caught
        if random.random() > self.get_risk(target_cell):
            self.do_crime(target_cell)
            print('Succes')
        else:
            self.get_caught()
            print('Caught')

class SsAgent(Agent):
    def __init__(self, pos, model, moore=False, sugar=0, metabolism=0, vision=0):
        super().__init__(pos, model)
        self.pos = pos
        self.moore = moore
        self.sugar = sugar
        self.metabolism = metabolism
        self.vision = vision

    def get_sugar(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is Sugar:
                return agent

    def is_occupied(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        return len(this_cell) > 1

    def move(self):
        # Get neighborhood within vision
        neighbors = [
            i
            for i in self.model.grid.get_neighborhood(
                self.pos, self.moore, False, radius=self.vision
            )
            if not self.is_occupied(i)
        ]
        neighbors.append(self.pos)
        # Look for location with the most sugar
        max_sugar = max(self.get_sugar(pos).amount for pos in neighbors)
        candidates = [
            pos for pos in neighbors if self.get_sugar(pos).amount == max_sugar
        ]
        # Narrow down to the nearest ones
        min_dist = min(get_distance(self.pos, pos) for pos in candidates)
        final_candidates = [
            pos for pos in candidates if get_distance(self.pos, pos) == min_dist
        ]
        self.random.shuffle(final_candidates)
        self.model.grid.move_agent(self, final_candidates[0])

    def eat(self):
        sugar_patch = self.get_sugar(self.pos)
        self.sugar = self.sugar - self.metabolism + sugar_patch.amount
        sugar_patch.amount = 0

    def step(self):
        self.move()
        self.eat()
        if self.sugar <= 0:
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)


class Sugar(Agent):
    def __init__(self, pos, model, max_sugar):
        super().__init__(pos, model)
        self.amount = max_sugar
        self.max_sugar = max_sugar

    def step(self):
        self.amount = min([self.max_sugar, self.amount + 10])

class Cop(Agent):
    n_cops=0
    def __init__(self, pos ,model, radius=1):
        super().__init__(pos, model)
        #self.id = id
        self.pos = pos

        self.n_cops += 1
        self.radius = radius

    # in the first notebook they use this:
    #def _init_(self, unique_id, model, pos):
        #super()._init_(unique_id, model)

    def new_cop(self):
        # this refers to the Model class we need
        self.model.new_agent(Cop, self.pos)
        Cop.n_cops += 1

    def remove_cop(self):
        # this also refers to the Model class we need
        # we may not end up removing any cops but still nice to have this function
        self.model.remove_agent(self)
        Cop.n_cops -= 1

    def city_part(self, position, city_part_per_grid_node):
        # this function returns the city part in which a cop is located
        pass

    def distribute_cops(self, cop_list, crime_rates, current_distr):
        # this determines distribution of cops over city parts, it is not the step function
        # this functions tells the step function how many cops have to switch city parts, so the closest cops can move
        # assume crite_rates is a dictionary with the number of crimes per city part, eg: dict = {'zuid': 42, 'oost': 32, 'noord': 50, 'west': 1000}
        total_crime = np.sum([i for i in crime_rates.values()])
        new_distribution =  {key: int(round(Cop.n_cops * value / total_crime)) for key, value in crime_rates.items()}
        return {key: int(round(value - current_distr[key])) for key, value in new_distribution.items()}

    def step(self, distribution_changes=None, positions_cops=None):
        # this function calls the distribute_cops function
        # this will be tough to figure out since the actual distribution of cops may not converge to the desired distribution in one period
        # then, cops in high crime areas may have to move to low crime areas so that other cops can move into the high crime area (if this leads to faster convergence)
        # for now they just randomly move
        
        possible_moves = self.model.grid.get_neighborhood(self.pos, moore=True,include_center=False, radius=self.radius)
        # could delete options outside the city part, e.g.:
        # for index, move in enumerate(possible moves):
            # if move.city_part != self.city_part():
                # possible_moves.del(index)
        new_pos = random.choice(possible_moves)
        self.model.grid.move_agent(self, new_pos)
        self.catch_criminal(1)

    def catch_criminal(self, city_part_surveillance):
        # catch radius will depend on city_part_surveillance, which i assume will be the radius of capturing
        # i assume a cop can only catch one criminal, and that only one criminal can be on a node of the grid
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True,include_center=True, radius=city_part_surveillance)
        #print("neighbours", str(neighbors))
        #contents_radius = [self.model.grid.get_cell_list_contents([position]) for position in neighbors]

        catchable_criminals = [obj for obj in neighbors if isinstance(obj, SsAgent)]
        print(catchable_criminals)
        if len(catchable_criminals) > 0:
            criminal_to_catch = self.random.choice(catchable_criminals)
            #print("Gonna catch em" + str(criminal_to_catch))
            # here remove some wealth from the criminal, for now minus one sugar for the ant
            # self.model.reduce_wealth(criminal_to_catch)
            criminal_to_catch.sugar -= 1000
            print("Gothca")
            # self.model.grid._remove_agent(criminal_to_catch.pos, criminal_to_catch)
            # self.model.schedule.remove(criminal_to_catch)
