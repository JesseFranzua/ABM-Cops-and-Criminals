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
    def __init__(
        self, pos, model, buddy_id=None, moore=True, wealth=100, 
        risk_aversion=1, search_radius=1, 
        risk_radius=5, jail_time=0, crimes_commited=0, does_crime=False
        ):
        super().__init__(pos, model)

        self.pos = pos
        self.wealth = wealth    
        self.risk_aversion = risk_aversion
        self.search_radius = search_radius
        self.jail_time = jail_time
        self.moore = moore
        self.risk_radius = risk_radius
        self.does_crime = does_crime
        self.crimes_commited = crimes_commited
        self.buddy_id = buddy_id
    
    def get_sugar(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is Sugar:
                return agent
                
    def get_wealth(self, pos):
        """
        Returns the wealth in a given cell
        """
        sugar_patch = self.get_sugar(pos)
        return sugar_patch.amount
    
    def get_risk(self, pos):
        """
        Returns the risk in a given cell
        TODO: determine risk_radius and risk per cop
        """
        risk = 0
        # district = self.model.get_district(pos)
        # district_risk = self.model.surveillance_levels[district]
        max_radius = self.risk_radius
        neighbors = self.model.grid.get_neighbors(pos, self.moore, True, max_radius)
        for n in neighbors:
            if type(n) is Cop:
                distance = get_distance(pos, n.pos)
                if distance == 0: # you are on the same cell as a cop
                    return 100
                risk += 1 / distance
        return risk
    
    def do_crime(self, pos):
        """
        Depletes the cell's resources and add them to the criminal's wealth
        """
        sugar_patch = self.get_sugar(pos)
        self.wealth += sugar_patch.amount
        self.crimes_commited +=1
        sugar_patch.amount = 0

    def get_utility(self, pos, a=1, b=1, c=0.3):
        wealth = self.get_wealth(pos)
        risk = self.get_risk(pos)
        distance = math.sqrt((pos[0] - self.pos[0]) ** 2 + (pos[1] - self.pos[1]) ** 2)
        distance = 0 if distance < 2 else distance # dont discriminate between cells in direct neighborhood
        own_wealth = self.wealth
        district = self.model.get_district(pos)
        district_risk = self.model.surveillance_levels[district]

        if own_wealth < 0:
            d = 0.5  # if your own wealth is negative you're more likely to commit crimes
        else:
            d = 0.01

        # print(f'a:{a*wealth} b:{b*risk} c:{c*distance} d:{d*own_wealth}')
        utility = a * wealth - b * district_risk * risk - c * distance - d * own_wealth
        # print(utility)
        return utility


    def step(self):
        '''
        The criminal makes an inventory of locations available to them,
        decides on where to go,
        moves to that location,
        and tries to do the crime.
        '''

        self.does_crime = False
        if self.jail_time > 0:
            self.jail_time -= 1
            return
        
        # get all surrounding cells
        own_neighborhood = self.model.grid.get_neighborhood(
            pos=self.pos, 
            moore=True, 
            include_center=True, 
            radius=self.search_radius
        )

        # get the utility of the neighbor cells
        utility_scores = {}
        for cell in own_neighborhood:
            utility_scores[cell] = self.get_utility(cell, b=self.risk_aversion)


        # get the utility of the cells of the buddies --- if very slow, only do this if there is no positive utility in own area
        for agents, x, y in self.model.grid.coord_iter():
            for agent in agents:
                if type(agent) is Criminal and (x, y) != self.pos:
                    if agent.buddy_id == self.buddy_id:
                        neighborhood = self.model.grid.get_neighborhood(
                            pos=(x, y), 
                            moore=True, 
                            include_center=True,
                            radius=self.search_radius
                        )
                        for cell in neighborhood:
                            utility_scores[cell] = self.get_utility(cell, b=self.risk_aversion)


        # determine the cell with the highest utility
        # print(f'Utility scores: {utility_scores}')
        highest_utility = max(utility_scores.values())
        possible_targets = [
            cell  
            for (cell, util) 
            in utility_scores.items() 
            if util == highest_utility
        ]

        # determine where to move
        make_buddy_move = False
        target_cell = random.choice(possible_targets)

        if target_cell not in own_neighborhood: 
            make_buddy_move = True
            if self.pos[0] > target_cell[0]:
                x_new = self.pos[0] - 1
            elif self.pos[0] < target_cell[0]:
                x_new = self.pos[0] + 1
            else: 
                x_new = self.pos[0]
            if self.pos[1] > target_cell[1]:
                y_new = self.pos[1] - 1
            elif self.pos[1] < target_cell[1]:
                y_new = self.pos[1] + 1
            else:
                y_new = self.pos[1]
            target_cell = (x_new, y_new)
          

        # move to the target cell
        self.model.grid.move_agent(self, target_cell)

        # do the crime
        if self.get_wealth(target_cell) > 0 and highest_utility > 0 and not make_buddy_move:
            self.does_crime = True
            self.do_crime(target_cell)
        else:
            self.does_crime = False

        #daily expenses
        self.wealth -= 20

class Sugar(Agent):
    def __init__(self, pos, model, max_sugar):
        super().__init__(pos, model)
        self.amount = max_sugar
        self.max_sugar = max_sugar

    def step(self):
        self.amount = self.max_sugar

class Cop(Agent):
    def __init__(self, pos, model, catch_radius=1, jail_sentence=10, id = np.random.random(), cop_stays_in_district=0, surveillance_radius=1):
        super().__init__(pos, model)
        self.pos = pos
        self.catch_radius = catch_radius
        self.jail_sentence = jail_sentence
        self.id = id
        self.cop_stays_in_district = cop_stays_in_district
        self.surveillance_radius = surveillance_radius

    def new_cop(self):
        self.model.new_agent(Cop, self.pos)
        self.model.n_cops += 1

    def remove_cop(self):
        # we may not end up removing any cops but still nice to have this function
        self.model.remove_agent(self)
        self.model.n_cops -= 1 

    def distribute_cops(self, crime_rates, current_distr):
        # this functions tells the step function how many cops have to switch city parts
        # assume crite_rates is a dictionary with the number of crimes per city part, eg: dict = {'zuid': 42, 'oost': 32, 'noord': 50, 'west': 1000}
        total_crime = np.sum([i for i in crime_rates.values()])
        nd_unrounded = {key: self.model.n_cops * value / total_crime for key, value in crime_rates.items()}
        nd_decimals = {key: value - math.floor(value) for key, value in nd_unrounded.items()}

        cops_left = self.model.n_cops - np.sum([math.floor(i) for i in nd_unrounded.values()])
        new_distribution = {}
        while cops_left > 0:
            for key, value in nd_unrounded.items():
                if nd_decimals[key] - math.floor(nd_decimals[key]) == max(nd_decimals.values()):
                    new_distribution[key] = math.ceil(nd_unrounded[key])
                    nd_decimals[key] = 0
                    cops_left -= 1
        for key in nd_decimals.keys():
            new_distribution[key] = math.floor(nd_unrounded[key])
        
        return {key: value - current_distr[key] for key, value in new_distribution.items()}

    def step(self):
        # when the first cop each step is asked to move, calculate the the distribution 
        #causes tango
        current_district = self.model.get_district(self.pos)
        self.surveillance_radius = self.model.surveillance_levels[current_district]
        if self.model.cops_that_stepped == 0:
            self.model.distribution_changes = self.distribute_cops(self.model.get_crimes_per_district(), self.model.get_agents_per_district(Cop))
            self.model.made_changes = {'Centrum': 0, 'Nieuw-West': 0, 'Noord': 0, 'Oost': 0, 'West': 0, 'Westpoort': 0, 'Zuid': 0, 'Zuidoost': 0, 'Undefined':0}
            self.model.districts_in_deficit = []
            self.model.districts_in_surplus = []
            for district, balance in self.model.distribution_changes.items():
                if balance > 0:
                    self.model.districts_in_deficit.append(district)
                elif balance < 0:
                    self.model.districts_in_surplus.append(district)
            self.model.cops_that_stepped += 1
            if self.model.n_cops == 1:
                self.model.cops_that_stepped = 0        
        
        else:
            self.model.cops_that_stepped += 1
            # set up cops_that_stepped for the next step period
            if self.model.cops_that_stepped == self.model.n_cops:
                self.model.cops_that_stepped = 0

        if self.cop_stays_in_district == 0:
            if self.model.distribution_changes != self.model.made_changes:
                district = self.model.get_district(self.pos)
                if district in self.model.districts_in_surplus:
                    self.model.made_changes[district] -= 1
                    new_district, new_pos, yes = self.new_district_move()
                    if yes == 'yes' and self.model.get_district(new_pos) != "Undefined":
                        self.model.made_changes[new_district] += 1
                        self.model.grid.move_agent(self, new_pos)
                        self.catch_criminal(1)
                    else:
                        self.move_to_crime()
                else:
                    self.move_to_crime()
            else:
                self.move_to_crime()
        else:
            self.move_to_crime()
            self.cop_stays_in_district -= 1

        new_district = self.model.get_district(self.pos)
        if current_district != new_district:
            self.cop_stays_in_district = 5

    def new_district_move(self):
        centers = {'Centrum': (32, 30), 'Nieuw-West': (9, 14), 'Noord': (31, 43), 'Oost': (40, 18), 'West': (23, 27), 'Westpoort': (12, 33), 'Zuid': (25, 11), 'Zuidoost': (45, 14)}
        distance_to_districts = {'Centrum': get_distance(self.pos, (32, 30)), 'Nieuw-West': get_distance(self.pos, (9, 14)), 
        'Noord': get_distance(self.pos, (31, 43)), 'Oost': get_distance(self.pos, (40, 18)), 'West': get_distance(self.pos, (23, 27)), 
        'Westpoort': get_distance(self.pos, (12, 33)), 'Zuid': get_distance(self.pos, (25, 11)), 'Zuidoost': get_distance(self.pos, (45, 14))}

        options = {}
        for key, value in distance_to_districts.items():
            if key in self.model.districts_in_deficit:
                options[key] = value
        min = 100 
        new_district = ''
        for key, value in options.items():
            if value < min:
                min = value
                new_district = key

        if new_district == '':
            return '', (0,0), 'no'
        else:

            if self.pos[0] > centers[new_district][0]:
                x_new = self.pos[0] - 1
            elif self.pos[0] < centers[new_district][0]:
                x_new = self.pos[0] + 1
            else: 
                x_new = self.pos[0]
            if self.pos[1] > centers[new_district][1]:
                y_new = self.pos[1] - 1
            elif self.pos[1] < centers[new_district][1]:
                y_new = self.pos[1] + 1
            else:
                y_new = self.pos[1]

            return new_district, (x_new, y_new), 'yes'

    def random_cop_move(self):
        possible_moves = self.model.grid.get_neighborhood(self.pos, moore=True,include_center=False, radius=1)
        # delete options outside the city part
        for index, move in enumerate(possible_moves):
            if self.model.get_district(move) != self.model.get_district(self.pos):
                del possible_moves[index]
        new_pos = random.choice(possible_moves)
        self.model.grid.move_agent(self, new_pos)
        self.catch_criminal(self.catch_radius)        
    
    def move_to_crime(self):
        # get moves in a large radius, delete those outside district, select the one with the lowest sugar
        possible_moves = self.model.grid.get_neighborhood(self.pos, moore=True,include_center=False, radius=self.surveillance_radius)
        possible_moves_dict = {}
        sugar_per_move = []
        feasible_moves = []
        for index, move in enumerate(possible_moves):
            #if self.model.get_district(move) != self.model.get_district(self.pos):
                #del possible_moves[index]
            if self.model.get_district(move) == self.model.get_district(self.pos):
                feasible_moves.append(move)
                # possible_moves_dict[self.get_sugar(move)] = move
                sugar_per_move.append(self.get_sugar(move))

        # sugar_per_move.sort()
        min_sugar_indices = np.where(sugar_per_move == np.min(sugar_per_move))[0]
        #changed this so that within the region it moves towards any of the low sugar areas
        direction = feasible_moves[random.choice(min_sugar_indices)]
        if self.model.get_district(direction) != self.model.get_district(self.pos):
            print("gaat hier al fout : ", direction)

        #direction = possible_moves_dict[sugar_per_move[0]]

        if self.pos[0] > direction[0]:
            if self.pos[0] - 2 >= 0:
                x_new = self.pos[0] - 2
            else:
                x_new = self.pos[0] - 1
        elif self.pos[0] < direction[0]:
            if self.pos[0] + 2 < 50:
                x_new = self.pos[0] + 2
            else:
                x_new = self.pos[0] + 1
        else:
            x_new = self.pos[0]
        if self.pos[1] > direction[1]:
            if self.pos[1] - 2 >= 0:
                y_new = self.pos[1] - 2
            else:
                y_new = self.pos[1] - 1
        elif self.pos[1] < direction[1]:
            if self.pos[1] + 2 < 50:
                y_new = self.pos[1] + 2
            else:
                y_new = self.pos[1] + 1
        else:
            y_new = self.pos[1]

        new_pos = (x_new, y_new)
        if self.model.get_district(new_pos) != self.model.get_district(self.pos):
            if (self.model.get_district((self.pos[0], self.pos[1] - 1)) != self.model.get_district(self.pos)) and (
                self.model.get_district((self.pos[0], self.pos[1] - 1)) == self.model.get_district(new_pos)
                ): # new district is below current district
                y_new = self.pos[1]
            elif (self.model.get_district((self.pos[0], self.pos[1] + 1)) != self.model.get_district(self.pos)) and (
                self.model.get_district((self.pos[0], self.pos[1] + 1)) == self.model.get_district(new_pos)
                ): # new district is above current district
                y_new = self.pos[1]
            elif (self.model.get_district((self.pos[0] - 1, self.pos[1])) != self.model.get_district(self.pos)) and (
                self.model.get_district((self.pos[0] - 1, self.pos[1])) == self.model.get_district(new_pos)
                ): # new district is to the left of the current district 
                x_new = self.pos[0]
            elif (self.model.get_district((self.pos[0] + 1, self.pos[1])) != self.model.get_district(self.pos)) and (
                self.model.get_district((self.pos[0] + 1, self.pos[1])) == self.model.get_district(new_pos) 
                ): # new district is to the right of the current district 
                x_new = self.pos[0]

            new_pos = (x_new, y_new)

        if(self.police_here(new_pos)):
            self.random_cop_move()
        else:
            self.model.grid.move_agent(self, new_pos)
            self.catch_criminal(self.catch_radius)   

    def police_here(self,pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is Cop:
                return True
        return False
        
    def get_sugar(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is Sugar:
                return int(agent.amount) 

    def get_max_sugar(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is Sugar:
                return int(agent.amount)     

    def catch_criminal(self, catch_radius):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True, radius=catch_radius)
        catchable_criminals = [obj for obj in neighbors if isinstance(obj, Criminal)]
        if len(catchable_criminals) > 0:
            criminal_to_catch = self.random.choice(catchable_criminals)         
            #if not yet in jail
            if(criminal_to_catch.jail_time==0 and criminal_to_catch.does_crime):
                criminal_to_catch.wealth -= self.get_max_sugar(criminal_to_catch.pos)
                criminal_to_catch.jail_time += self.jail_sentence