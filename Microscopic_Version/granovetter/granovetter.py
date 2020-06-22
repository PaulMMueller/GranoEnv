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
            self,number_of_nodes=200,average_degree=10,
            upper_social_threshold=0.6, lower_social_threshold=0.5,
            upper_pollution_threshold=0.4, lower_pollution_threshold=0.3, 
            time_horizon=1000, vulnerability=0.1, farsightness=10,
            delta_t=1e-4, integration_time=10, 
            initial_pollution = 0, initial_average_activity = 0,
            model='ER',small_worldness_parameter = 1,
            verbose = True):
        '''

        Parameters
        ----------
        number_of_nodes : Integer, optional
            Number of nodes of the network of agents. 
            The default is 200.
        average_degree : Float, optional
            Average number of idrect neighbours the agents have. Has to be an even integer if the WS model is used.
            The default is 10.
        upper_social_threshold : Float, optional
            Upper social threshold.
            The default is 0.6.
        lower_social_threshold : Float, optional
            Lower social threshold.
            The default is 0.5.
        upper_pollution_threshold : Float, optional
            Upper pollution threshold.
            The default is 0.4.
        lower_pollution_threshold : Float, optional
            Lower pollution threshold. The default is 0.3.
        time_horizon : Float, optional
            Anticipation time up to which the agents evaluate the future.
            The default is 1000.
        vulnerability : Float, optional
            Weight for the action due to direct environmental impacts.
            The default is 0.1.
        farsightness : Float, optional
            Weight for the action due to social contagion and anticipated environmental impacts.
            The default is 10.
        delta_t : Float, optional
            Time step width.
            The default is 1e-4.
        integration_time : Float, optional
            Time up to which the model is integrated. Can be changed before the model is evolved in time.
            The default is 10.
        initial_pollution : Float, optional
            Initial value of the pollution. The default is 0.
        initial_average_activity : Float, optional
            Initial share of active agents. Will be rounded to fit a possible value for the given network.
            The default is 0.
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
        self.upper_social_threshold = upper_social_threshold       
        self.lower_social_threshold = lower_social_threshold
  
        self.upper_pollution_threshold = upper_pollution_threshold
        self.lower_pollution_threshold = lower_pollution_threshold

        self.time_horizon = time_horizon   #Keep in mind that time horizon takes acutal time units and is not multiplied by delta_t
        self.vulnerability = vulnerability
        self.farsightness = farsightness

        # Starting parameters
        self.initial_pollution = initial_pollution
        self.initial_average_activity = initial_average_activity
        # Time evolution properties
        self.delta_t = delta_t
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
        self.average_activity = self.get_average_activity()
        self.time = 0
        self.pollution_change = 1-self.average_activity -self.pollution
        self.node_change_list = []
        
        # Save properties
        self.verbose = verbose
        if verbose:
            print('Full output on.')
        else:
            print('Full output off.')
        #If not False give how many data points should be skipped until the next is printed 

    def __make_initial_active_nodes(self): 
        ''' Draw random initial active nodes
        '''
        number_of_initial_active_nodes = int(np.round(self.initial_average_activity*self.number_of_nodes))
        self.initial_active_list = random.sample(range(0,self.number_of_nodes),number_of_initial_active_nodes) 
        
        return self.initial_active_list
    
    def __make_ER_network(self):
        '''Initaite the Erdos-Renyi type random network. 
        '''
        link_probability = self.average_degree/(self.number_of_nodes-1)
        self.network = nx.erdos_renyi_graph(n=self.number_of_nodes,p =link_probability)
        for i in range(self.number_of_nodes):
            self.network.nodes()[i]['activity'] = False 
        for i in self.__make_initial_active_nodes():
            self.network.nodes()[i]['activity'] = True
            
    def __make_WS_network(self):
        '''Initiate the Watts-Strogatz type network
        '''
        self.network = nx.watts_strogatz_graph(n=self.number_of_nodes, k=self.average_degree,
                                                         p = self.small_worldness_parameter)
        for i in range(self.number_of_nodes):
            self.network.nodes()[i]['activity'] = False 


        for i in self.__make_initial_active_nodes():
            self.network.nodes()[i]['activity'] = True
         
      
        
    def get_average_activity(self):
        ''' Return the average activity X of the network
        '''
        number_of_active_nodes = 0
        node_data = self.network.nodes.data()
        for data in node_data:
            active = data[1]['activity']
            if active:
                number_of_active_nodes +=1
        return number_of_active_nodes/self.number_of_nodes
    
    def DGL_Pollution(self,average_activity=None):  
        ''' Give the solution of the equation for the derivative of the pollution. If None is the
        '''
        if average_activity == None:
            average_activity = self.average_activity
            return (1-average_activity) - self.pollution
        else:
            return (1-average_activity) - self.pollution
        
    def Pollution_after_time(self,time):
        '''Plug the time in the analytical solution of the pollution and return the pollution after that time.
        '''
        X = self.average_activity
        Y = self.pollution
        t = time
        
        return (1-X) - (1-X-Y)*np.exp(-t)
        
    def get_activity_degree(self,node_number):
        '''Get the number of active neighbors of the node {node_number}
        '''
        neighbors = self.network.neighbors(node_number)
        active_neighbors = 0
        for i in neighbors:
            if self.network.nodes[i]['activity']:
                active_neighbors +=1           
        return active_neighbors

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
        social_trigger = 0
        pollution_trigger = 0
        horizon_trigger = 0
        
        active_neighbors = self.get_activity_degree(node_number)
        ndegree = self.network.degree[node_number]
      
        # Change probability for not active nodes to become active
        if not self.network.nodes[node_number]['activity']:
            # Check for which threshold is exceded and set the corresponding trigger to 1
            if active_neighbors >= ndegree*self.upper_social_threshold:
                social_trigger = 1
            if self.pollution >= self.upper_pollution_threshold:
                pollution_trigger = 1
            if (self.pollution+self.time_horizon*self.pollution_change) >= self.upper_pollution_threshold:
                horizon_trigger = 1
            return self.vulnerability*pollution_trigger +social_trigger*self.farsightness*horizon_trigger
        
        # Change probability for active nodes to become inactive
        else:
            if active_neighbors < ndegree*self.lower_social_threshold:
                social_trigger = 1
            if self.pollution < self.lower_pollution_threshold:
                pollution_trigger = 1
            if (self.pollution+self.time_horizon*self.pollution_change) < self.lower_pollution_threshold:
                horizon_trigger = 1
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
            self.average_activity = self.get_average_activity()
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
        
        print(f'''TG {self.model} for \nNodes {self.number_of_nodes}, Average Degree {self.average_degree}, Rewiring probability (only WS) {self.small_worldness_parameter},
Upper_social_threshold {self.upper_social_threshold},
Lower_social_threshold {self.lower_social_threshold},
Upper_pollution_threshold {self.upper_pollution_threshold},
Lower_pollution_threshold {self.lower_pollution_threshold},
Time_horizon {self.time_horizon},
Vulnerability {self.vulnerability}, Farsightness {self.farsightness},
Initial_Pollution {self.initial_pollution}, Initial_Average_Activity {self.initial_average_activity},
Delta_t {self.delta_t}, Integration_time {self.integration_time}\n''')
        self.get_average_shortest_path_length()
        self.get_clustering_coefficient()
        self.get_connectivity()
        print(f'Active_node_list: {self.initial_active_list}')
        print(f'Adjacency matrix: {self.get_adjacency_matrix()}\n')

        print('Time, Pollution, Average Activity, Changing nodes')
        print(f'{self.time},{self.pollution},{self.average_activity}, {self.node_change_list}') 
        
    def print_time_step(self):
        print(f'{self.time},{self.pollution},{self.average_activity},{self.node_change_list}')
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
