from collections import defaultdict

from mesa.time import RandomActivation

from agents import Criminal

class RandomActivationByBreed(RandomActivation):
    """
    A scheduler which activates each type of agent once per step, in random
    order, with the order reshuffled every step.

    This is equivalent to the NetLogo 'ask breed...' and is generally the
    default behavior for an ABM.

    Assumes that all agents have a step() method.
    """

    def __init__(self, model):
        super().__init__(model)
        self.agents_by_breed = defaultdict(dict)

    def add(self, agent):
        """
        Add an Agent object to the schedule

        Args:
            agent: An Agent to be added to the schedule.
        """

        self._agents[agent.unique_id] = agent
        agent_class = type(agent)
        self.agents_by_breed[agent_class][agent.unique_id] = agent

    def remove(self, agent):
        """
        Remove all instances of a given agent from the schedule.
        """

        del self._agents[agent.unique_id]

        agent_class = type(agent)
        del self.agents_by_breed[agent_class][agent.unique_id]

    def step(self, by_breed=True):
        """
        Executes the step of each agent breed, one at a time, in random order.

        Args:
            by_breed: If True, run all agents of a single breed before running
                      the next one.
        """
        #Order is first sugar, then criminal, then cop
        if by_breed:
            for agent_class in self.agents_by_breed:
                self.step_breed(agent_class)
            self.steps += 1
            self.time += 1
        else:
            super().step()

    def step_breed(self, breed):
        """
        Shuffle order and run all agents of a given breed.

        Args:
            breed: Class object of the breed to run.
        """
        agent_keys = list(self.agents_by_breed[breed].keys())
        self.model.random.shuffle(agent_keys)
        for agent_key in agent_keys:
            self.agents_by_breed[breed][agent_key].step()

    def get_breed_count(self):
        """
        Returns the current number of agents of certain breed in the queue.
        """
        total_wealth = 0
        for agent in self.model.schedule.agents:
            if type(agent) is Criminal:
                total_wealth += agent.wealth
        return total_wealth
        #return len(self.agents_by_breed[breed_class].values())

    def get_criminal_count(self):
        return len(self.agents_by_breed[Criminal].values())

    def get_criminal_count_in_jail(self):
        count = 0
        for agent in self.model.schedule.agents:
            if type(agent) is Criminal:
                if agent.jail_time > 0:
                    count+=1
        return count

    def get_crimes_commited(self):
        count = 0
        for agent in self.model.schedule.agents:
            if type(agent) is Criminal:
                    count+=agent.crimes_commited
        return count
    
    def get_crimes_per_timestep(self):
        return self.model.get_crimes_per_district()
    
    def update_average_crimes_per_timestep(self,district):
        return self.model.update_average_crimes_per_district(district)

    
