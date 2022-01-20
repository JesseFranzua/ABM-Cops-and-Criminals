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
    # TODO: optimize, its slow
    def __init__(
        self, pos, model, moore=True, wealth=100, 
        risk_tolerance=0.5, search_radius=1, 
        risk_radius=2, jail_time=0,crimes_commited=0, does_crime=False
        ):
        super().__init__(pos, model)

        self.pos = pos
        self.wealth = wealth
        self.risk_tolerance = risk_tolerance
        self.search_radius = search_radius
        self.jail_time = jail_time
        self.moore = moore
        self.risk_radius = risk_radius
        self.does_crime = does_crime
        self.crimes_commited = crimes_commited
    
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
        n_cops_around = 0
        neighbors = self.model.grid.get_neighbors(pos, self.moore, True, self.risk_radius)
        for n in neighbors:
            if type(n) is Cop:
                n_cops_around += 1
        risk = n_cops_around * 0.1
        return risk
    
    def do_crime(self, pos):
        """
        Depletes the cell's resources and add them to the criminal's wealth
        """
        sugar_patch = self.get_sugar(self.pos)
        self.wealth += sugar_patch.amount
        self.crimes_commited +=1
        sugar_patch.amount = 0

    def get_utility(self, pos):
        # if you have a lot of money already,
        # only go after high paying jobs
        utility = math.log(self.get_wealth(pos) + 1)
        return utility


    def step(self):
        '''
        The criminal makes an inventory of locations available to them,
        decides on where to go,
        moves to that location,
        and tries to do the crime.
        '''
        # print("YOOO")
        if self.jail_time > 0:
            self.jail_time -= 1
            return
        
        # get all surrounding cells, can extend to cells of other criminals in the network
        neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=True, radius=self.search_radius
        )


        # filter the cells that have an acceptable risk 
        utility_treshold = self.wealth / 1000
        options = [cell for cell in neighborhood if self.get_risk(cell) < self.risk_tolerance and self.get_utility(cell) > utility_treshold]
        # print(options)
        if len(options) == 0:
            self.does_crime = False
            return

        # determine which cell has the most wealth
        wealth = [self.get_wealth(cell) for cell in options]
        # print(wealth)
        if(all(element == wealth[0] for element in wealth)):
            target_cell = random.choice(options)
        else:
            max_wealth_indices = np.where(wealth == np.max(wealth))[0]
            target_cell = options[random.choice(max_wealth_indices)]
        # print(target_cell)
        # move the criminal to the target cell
        self.model.grid.move_agent(self, target_cell)

        # do the crime
        if self.get_wealth(target_cell) > 0:
            self.does_crime = True
            self.do_crime(target_cell)
            #print('Succes')
        else:
            self.does_crime = False
            #print('Didnt steal')
            
    

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
    def __init__(self, pos ,model, radius=1, id = np.random.random()):
        super().__init__(pos, model)
        self.pos = pos
        self.radius = radius
        self.id = id 

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
        if self.model.cops_that_stepped == 0:
            print('n_cops:', self.model.n_cops)
            print('current distribution:', self.model.get_agents_per_district(Cop))
            self.model.distribution_changes = self.distribute_cops(self.model.get_crimes_per_district(), self.model.get_agents_per_district(Cop))
            print('crimes per district:', self.model.get_crimes_per_district())
            print('disttribution changes:', self.model.distribution_changes)
            self.model.made_changes = {'Centrum': 0, 'Nieuw-West': 0, 'Noord': 0, 'Oost': 0, 'West': 0, 'Westpoort': 0, 'Zuid': 0, 'Zuidoost': 0, 'Undefined':0}
            self.model.districts_in_deficit = []
            self.model.districts_in_surplus = []
            for district, balance in self.model.distribution_changes.items():
                print('10', district, balance)
                if balance > 0:
                    print('20', district)
                    self.model.districts_in_deficit.append(district)
                elif balance < 0:
                    print('30', district)
                    self.model.districts_in_surplus.append(district)
            self.model.cops_that_stepped += 1
        
        else:
            self.model.cops_that_stepped += 1
            # set up cops_that_stepped for the next step period
            if self.model.cops_that_stepped == self.model.n_cops:
                self.model.cops_that_stepped = 0

        if self.model.distribution_changes != self.model.made_changes:
            district = self.model.get_district(self.pos)
            print(district, self.model.districts_in_surplus)
            if district in self.model.districts_in_surplus:
                self.model.made_changes[district] -= 1
                new_district, new_pos, yes = self.new_district_move()
                if yes == 'yes':
                    print('8000', new_district, self.pos, new_pos)
                    self.model.made_changes[new_district] += 1
                    self.model.grid.move_agent(self, new_pos)
                    self.catch_criminal(1)   
                else:
                    print('7000')
                    self.random_cop_move() 
            else:
                print('9000')
                self.random_cop_move()
        
        else:
            self.random_cop_move()
            print('10000')

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
        possible_moves = self.model.grid.get_neighborhood(self.pos, moore=True,include_center=False, radius=self.radius)
        # delete options outside the city part
        for index, move in enumerate(possible_moves):
            if self.model.get_district(move) != self.model.get_district(self.pos):
                del possible_moves[index]
        new_pos = random.choice(possible_moves)
        self.model.grid.move_agent(self, new_pos)
        self.catch_criminal(1)        

    def catch_criminal(self, city_part_surveillance):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True,include_center=True, radius=city_part_surveillance)
        catchable_criminals = [obj for obj in neighbors if isinstance(obj, Criminal)]
        if len(catchable_criminals) > 0:
            criminal_to_catch = self.random.choice(catchable_criminals)
            
            #if not yet in jail
            if(criminal_to_catch.jail_time==0 and criminal_to_catch.does_crime):
                criminal_to_catch.wealth -= 100
                criminal_to_catch.jail_time += 5
                #print("Gothca")
            # self.model.grid._remove_agent(criminal_to_catch.pos, criminal_to_catch)
            # self.model.schedule.remove(criminal_to_catch)