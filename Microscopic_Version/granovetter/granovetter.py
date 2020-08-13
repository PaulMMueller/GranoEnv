# -*- coding: utf-8 -*-


'''
Threshold Graonvetter as in the Master Thesis of Paul Manuel Müller

Y' = 1-X-Y

Change probability rates
p_+i = alpha*1_(Y>=Y_+) + 1_(z_i>= k_i*g)*beta*1_(Y+Y'*theta>=Y_+)
p_-i = alpha*1_(Y<Y_-) + 1_(z_i < k_i*g)*beta*1 _(Y+Y'*theta<Y_-)

'''
import networkx as nx
import numpy as np
np.set_printoptions(threshold=np.inf)
import random 
class granovetter:
    
    def __init__(
            self,
            social_threshold=0.6, pollution_threshold=0.4, 
            vulnerability=0.1, farsightness=10, time_horizon=1000,
            tau = 1,
            delta_t=1e-4, integration_time=10, 
            initial_pollution = 0.0, initial_average_inactivity = 0.0,
            number_of_nodes=200,average_degree=10,
            model='ER',small_worldness_parameter = 1.0,
            verbose = True):
        '''

        Parameters
        ----------
        
        social_threshold : Float, optional
            Social threshold.
            The default is 0.6.
        pollution_threshold : Float, optional
            Pollution threshold.
            The default is 0.4.
        lower_pollution_threshold : Float, optional
            Lower pollution threshold. The default is 0.3.
        vulnerability : Float, optional
            Weight for the action due to direct environmental impacts.
            The default is 0.1.
        farsightness : Float, optional
            Weight for the action due to social contagion and anticipated environmental impacts.
            The default is 10.
        time_horizon : Float, optional
            Anticipation time up to which the agents evaluate the future.
            The default is 1000.
        tau : Float, optional
            Lifetime of the ecological dynamics
        delta_t : Float, optional
            Time step width.
            The default is 1e-4.
        integration_time : Float, optional
            Time up to which the model is integrated. Can be changed before the model is evolved in time.
            The default is 10.
        initial_pollution : Float, optional
            Initial value of the pollution. The default is 0.
        initial_average_inactivity : Float, optional
            Initial share of INactive agents. Will be rounded to fit a possible value for the given network.
            The default is 0.
        number_of_nodes : Integer, optional
            Number of nodes of the network of agents. 
            The default is 200.
        average_degree : Float, optional
            Average number of idrect neighbours the agents have. Has to be an even integer if the WS model is used.
            The default is 10.
        model : String, optional
            Network constrcution method.  Either Eros-Renyi 'ER' or Watts-Strogatz 'WS'.
            The default is 'ER'.
        small_worldness_parameter : Float, optional
            Rewiring probability for the Watts-Storgatz model. Will be ignored if the model is ER.
            The default is 1.
        verbose : Bool, optional
            Determines if every time step is printed. 
            The default is True.


        Returns
        -------
        None.

        '''
        print('Initialize GranoEnv Instance')
        # Model properties
        self.social_threshold = social_threshold       

  
        self.pollution_threshold = pollution_threshold

        self.time_horizon = time_horizon   #Keep in mind that time horizon takes acutal time units and is not multiplied by delta_t
        self.vulnerability = vulnerability
        self.farsightness = farsightness

        self.tau = tau
        # Starting parameters
        self.initial_pollution = initial_pollution
        self.initial_average_inactivity = initial_average_inactivity
        # Time evolution properties
        self.delta_t = delta_t
        self.time_precision = int(np.log10(1/delta_t))
        self.integration_time = integration_time
        self.time_steps = int(self.integration_time/self.delta_t) # Convert integartion time with step width to the number of time_steps
        
        #Network properties
        self.number_of_nodes =  number_of_nodes
        self.average_degree = average_degree
        self.network = None
        self.small_worldness_parameter = small_worldness_parameter
        self.model = model
        if self.model == 'ER':
            self.__make_ER_network()
        elif self.model == 'WS':
            if int(self.average_degree)%2!=0:
                raise Exception('Average degree has to be an even integer if WS model is used.')
            else:
                self.__make_WS_network()
        else:
            raise Exception('Invalid network model.')
        # Outcome preparation
        self.pollution = initial_pollution
        self.average_inactivity = self.get_average_inactivity()
        self.time = 0
        self.pollution_change = (self.average_inactivity -self.pollution)/self.tau
        self.node_change_list = []
        
        # Save properties
        self.verbose = verbose
        if verbose:
            print('Full output on.')
        else:
            print('Full output off.')
        #If not False give how many data points should be skipped until the next is printed 

    def __make_initial_inactive_list(self): 
        ''' Draw random initial active nodes
        '''
        number_of_initial_inactive_nodes = int(np.round(self.initial_average_inactivity*self.number_of_nodes))
        self.initial_inactive_list = sorted(random.sample(range(0,self.number_of_nodes),number_of_initial_inactive_nodes))
        
        return self.initial_inactive_list
    
    def __make_ER_network(self):
        '''Initiate the Erdos-Renyi type random network. 
        '''
        link_probability = self.average_degree/(self.number_of_nodes-1)
        self.network = nx.erdos_renyi_graph(n=self.number_of_nodes,p =link_probability)
        for i in range(self.number_of_nodes):
            self.network.nodes()[i]['activity'] = True
        for i in self.__make_initial_inactive_list():
            self.network.nodes()[i]['activity'] = False
            
    def __make_WS_network(self):
        '''Initiate the Watts-Strogatz type network
        '''
        self.network = nx.watts_strogatz_graph(n=self.number_of_nodes, k=self.average_degree,
                                                         p = self.small_worldness_parameter)
        for i in range(self.number_of_nodes):
            self.network.nodes()[i]['activity'] = True


        for i in self.__make_initial_inactive_list():
            self.network.nodes()[i]['activity'] = False
         
      
        
    def get_average_inactivity(self):
        ''' Return the average inactivity X of the network
        '''
        number_of_inactive_nodes = 0
        node_data = self.network.nodes.data()
        for data in node_data:
            active = data[1]['activity']
            if not active:
                number_of_inactive_nodes +=1
        return number_of_inactive_nodes/self.number_of_nodes
    
    def DGL_Pollution(self,average_inactivity=None):  
        ''' Give the solution of the equation for the derivative of the pollution. If None is the
        '''
        if average_inactivity == None:
            average_inactivity = self.average_inactivity
            return (average_inactivity - self.pollution)/self.tau
        else:
            return (average_inactivity - self.pollution)/self.tau
        
    def Pollution_after_time(self,time):
        '''Plug the time in the analytical solution of the pollution and return the pollution after that time.
        '''
        X = self.average_inactivity
        Y = self.pollution
        t = time
        
        return X - (X-Y)*np.exp(-t/self.tau)
        
    def get_inactivity_degree(self,node_number):
        '''Get the number of inactive neighbors of the node {node_number}
        '''
        neighbors = self.network.neighbors(node_number)
        inactive_neighbors = 0
        for i in neighbors:
            if not self.network.nodes[i]['activity']:
                inactive_neighbors +=1           
        return inactive_neighbors

    def __get_change_of_activity(self,probabilty):
        '''Chose a random number and compare it to the proability to generate a True/False for the node switching
        '''
        return np.random.random() < probabilty
    
    def get_change_probability(self, node_number):
        '''
        Calculate the change probability for node {node_number}=i
        Change probability rates
        p_+i = alpha*1_(Y>=Y_+) + 1_(z_i>= k_i*g)*beta*1_(Y+Y'*theta>=Y_+)
        p_-i = alpha*1_(Y<Y_-) + 1_(z_i < k_i*g)*beta*1 _(Y+Y'*theta<Y_-)
        
        '''

        
        inactive_neighbors = self.get_inactivity_degree(node_number)
        ndegree = self.network.degree[node_number]
      
        # Change probability for not active nodes to become active
        if not self.network.nodes[node_number]['activity']:
            # Check for which threshold is exceded and set the corresponding trigger to 1
            social_trigger = (inactive_neighbors < ndegree*self.social_threshold)
            pollution_trigger = (self.pollution >= self.pollution_threshold)
            horizon_trigger = ((self.pollution+self.time_horizon*self.pollution_change) >= self.pollution_threshold)
            return self.vulnerability*pollution_trigger +social_trigger*self.farsightness*horizon_trigger
        
        # Change probability for active nodes to become inactive
        else:
            social_trigger = (inactive_neighbors >= ndegree*self.social_threshold)
            pollution_trigger = (self.pollution < self.pollution_threshold)
            horizon_trigger = ((self.pollution+self.time_horizon*self.pollution_change) < self.pollution_threshold)
            return self.vulnerability*pollution_trigger + social_trigger*self.farsightness*horizon_trigger
 

    
    def evolve_in_time(self):
        '''Make all the time steps
        '''
        self.print_header()    


                  
        for time_width in np.full(shape = self.time_steps, fill_value = self.delta_t):
            #Calculate the pollution change with the actuale DGL
            self.pollution_change = self.DGL_Pollution()
          
            #Calculate the change of activity for every node. 
            change_probabilities = [] # Make a list first so that only interactions with the activities of the old time step are possible.
            for i in range(0,self.number_of_nodes):
                change_probabilities.append(self.get_change_probability(i)*time_width)
            for i in range(0,self.number_of_nodes):        
                if self.__get_change_of_activity(change_probabilities[i]):
                    self.node_change_list.append(i)
                    if self.network.nodes()[i]['activity']:
                         self.network.nodes()[i]['activity'] = False
                    else:
                        self.network.nodes()[i]['activity'] = True

            #Update the data 
            self.average_inactivity = self.get_average_inactivity()
            self.pollution = self.Pollution_after_time(time_width)
            self.time +=time_width
            
            # Print the model Data
            if self.verbose:
                self.print_time_step()
            else:
                pass     
  
    def print_header(self):
        '''Prints the header with all model and numerical parameters
        '''
        
        print(f'''
Pollution Threshold: {self.pollution_threshold}
Social Threshold: {self.social_threshold}

Vulnerability: {self.vulnerability}
Farsightedness: {self.farsightness}
Time Horizon: {self.time_horizon}

Lifetime of the ecological dynamics: {self.tau}
Step Size: {self.delta_t}
Integration Time: {self.integration_time}

Initial_Pollution: {self.initial_pollution}
Initial_Average_Inactivity {self.initial_average_inactivity}

Model: {self.model}
Nodes: {self.number_of_nodes}
Average Degree: {self.average_degree}
Rewiring probability (only WS): {self.small_worldness_parameter}\n''')
        self.get_average_shortest_path_length()
        self.get_clustering_coefficient()
        self.get_connectivity()
        print(f'Inactive_node_list: {self.initial_inactive_list}')
        print(f'Adjacency matrix: {self.get_adjacency_matrix()}\n')

        print('Time, Average Inactivity, Pollution,  Changing nodes')
        print(f'{self.time:.{self.time_precision}f}, {self.average_inactivity:.6f}, {self.pollution:.6f}, {self.node_change_list}') 
        
    def print_time_step(self):
        print(f'{self.time:.{self.time_precision}f}, {self.average_inactivity:.6f}, {self.pollution:.6f}, {self.node_change_list}')
        self.node_change_list = [] # Resets the node change list. Is importanted to be done here due to the sparse data.

            
    '''Methods to call model outcome'''
    def get_pollution_and_set_end_flag(self):
        '''Prints the current pollution and average waiting time until now
        '''
        self.print_time_step() 
        print(f'===CalculationEnded===')
        
    def get_clustering_coefficient(self):
        clustering_coefficient = nx.average_clustering(self.network)
        print(f'Clustering_coefficient: {clustering_coefficient}')
        return clustering_coefficient

    def get_adjacency_matrix(self):
        return nx.to_numpy_matrix(self.network)

    def get_connectivity(self):
        con = nx.is_connected(self.network)
        print(f'Connected: {con}')
        return con        

    def get_average_shortest_path_length(self):
        try:
            av_sh_pa_le = nx.average_shortest_path_length(self.network)
            print(f'Average shortest path length is, {av_sh_pa_le}')
        except:
            print(f'Average shortest path length is not defined. Network is not connected.') 
