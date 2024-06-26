"""Network controller"""

import numpy as np
import farms_pylog as pylog
import metrics


class WaveController:

    """Test controller"""

    def __init__(self, pars):
        self.pars = pars
        self.timestep = pars.timestep
        self.times = np.linspace(
            0,
            pars.n_iterations *
            pars.timestep,
            pars.n_iterations)
        self.n_joints = pars.n_joints

        # state array for recording all the variables
        self.state = np.zeros((pars.n_iterations, 2*self.n_joints))
       
        # indexes of the left muscle activations (optional)
        self.muscle_l = 2*np.arange(15)
        # indexes of the right muscle activations (optional)
        self.muscle_r = self.muscle_l+1
        self.metrics = metrics.compute_controller(self)

    def S_sqrt(self, x):
        return np.sqrt(np.maximum(x,0))

    def S_max(self, x):
        return np.maximum(x,0)

    def S_sigmoid(self, x,lam,theta):
        return 1/(1+np.exp(-lam*(x-theta)))
    


    def step(self, iteration, time, timestep, pos=None):
        """
        Step function. This function passes the activation functions of the muscle model
        Inputs:
        - iteration - iteration index
        - time - time vector
        - timestep - integration timestep
        - pos (not used) - joint angle positions

        Implement here the control step function,
        it should return an array of 2*n_joint=30 elements,
        even indexes (0,2,4,...) = left muscle activations
        odd indexes (1,3,5,...) = right muscle activations

        In addition to returning the activation functions, store
        them in self.state for later use offline
        """

        if self.pars.activation_func[0]:
            array = np.zeros(2*self.n_joints)
            array[self.muscle_r] = self.S_sigmoid(0.5 - (self.pars.amp/2)*np.sin(2*np.pi*(self.pars.freq*time - self.pars.wavefrequency*((self.muscle_r-1)/(2*self.n_joints)))), self.pars.activation_func[1],self.pars.activation_func[2])
            array[self.muscle_l] = self.S_sigmoid(0.5 + (self.pars.amp/2)*np.sin(2*np.pi*(self.pars.freq*time - self.pars.wavefrequency*(self.muscle_l/(2*self.n_joints)))), self.pars.activation_func[1],self.pars.activation_func[2])
            self.state[iteration,:] = array
            return array
        else: 
            array = np.zeros(2*self.n_joints)
            array[self.muscle_r] = 0.5 - (self.pars.amp/2)*np.sin(2*np.pi*(self.pars.freq*time - self.pars.wavefrequency*((self.muscle_r-1)/(2*self.n_joints))))
            array[self.muscle_l] = 0.5 + (self.pars.amp/2)*np.sin(2*np.pi*(self.pars.freq*time - self.pars.wavefrequency*(self.muscle_l/(2*self.n_joints))))
            self.state[iteration,:] = array
            return array

    
    
    