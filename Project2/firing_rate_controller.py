"""Network controller"""

import numpy as np
from scipy.interpolate import CubicSpline
import scipy.stats as ss
import farms_pylog as pylog
import metrics

class FiringRateController:
    """zebrafish controller"""

    def __init__(
            self,
            pars
    ):
        super().__init__()

        self.n_iterations = pars.n_iterations
        self.n_neurons = pars.n_neurons
        self.n_muscle_cells = pars.n_muscle_cells
        self.timestep = pars.timestep
        self.times = np.linspace(
            0,
            self.n_iterations *
            self.timestep,
            self.n_iterations)
        self.pars = pars

        self.n_eq = self.n_neurons*4 + self.n_muscle_cells*2 + self.n_neurons * \
            2  # number of equations: number of CPG eq+muscle cells eq+sensors eq
        self.muscle_l = 4*self.n_neurons + 2 * \
            np.arange(0, self.n_muscle_cells)  # muscle cells left indexes
        self.muscle_r = self.muscle_l+1  # muscle cells right indexes
        self.all_muscles = 4*self.n_neurons + \
            np.arange(0, 2*self.n_muscle_cells)  # all muscle cells indexes
        # vector of indexes for the CPG activity variables - modify this
        # according to your implementation

        

        self.L_v= np.arange(self.n_neurons)
        self.R_v= self.n_neurons + np.arange(self.n_neurons)
        self.all_v = np.concatenate([self.L_v,self.R_v])
        self.all_a= 2*self.n_neurons + np.arange(0, self.n_neurons*2)
        self.L_a= 2*self.n_neurons + np.arange(0, self.n_neurons)
        self.R_a= 3*self.n_neurons + np.arange(0, self.n_neurons)
        self.all_s=self.n_neurons*4 + self.n_muscle_cells*2 + np.arange(0, self.n_neurons*2)
        self.L_s=self.n_neurons*4 + self.n_muscle_cells*2 + np.arange(0, self.n_neurons)
        self.R_s=self.n_neurons*4 + self.n_muscle_cells*2 + self.n_neurons + np.arange(0, self.n_neurons)


        self.state = np.zeros([self.n_iterations, self.n_eq])  # equation state
        self.dstate = np.zeros([self.n_eq])  # derivative state
        self.state[0] = np.random.rand(self.n_eq)  # set random initial state

        self.poses = np.array([
            0.007000000216066837,
            0.00800000037997961,
            0.008999999612569809,
            0.009999999776482582,
            0.010999999940395355,
            0.012000000104308128,
            0.013000000268220901,
            0.014000000432133675,
            0.014999999664723873,
            0.01600000075995922,
        ])  # active joint distances along the body (pos=0 is the tip of the head)

        self.poses_ext = np.linspace(
            self.poses[0], self.poses[-1], self.n_neurons)  # position of the sensors

        # initialize ode solver
        if self.pars.stretch:
            self.f = self.ode_rhs
        else:
            self.f = self.ode_rhs_bis

        # stepper function selection
        if self.pars.method == "euler":
            self.step = self.step_euler
        elif self.pars.method == "noise":
            self.step = self.step_euler_maruyama
            # vector of noise for the CPG voltage equations (2*n_neurons)
            self.noise_vec = np.zeros(self.n_neurons*2)

        # zero vector activations to make first and last joints passive
        # pre-computed zero activity for the first 4 joints
        self.zeros8 = np.zeros(8)
        # pre-computed zero activity for the tail joint
        self.zeros2 = np.zeros(2)

        #adding metrics
        self.metrics = metrics.compute_controller(self)

    def get_ou_noise_process_dw(self, timestep, x_prev, sigma):
        """
        Implement here the integration of the Ornstein-Uhlenbeck processes
        dx_t = -0.5*x_t*dt+sigma*dW_t
        Parameters
        ----------
        timestep: <float>
            Timestep
        x_prev: <np.array>
            Previous time step OU process
        sigma: <float>
            noise level
        Returns
        -------
        x_t{n+1}: <np.array>
            The solution x_t{n+1} of the Euler Maruyama scheme
            x_new = x_prev-0.1*x_prev*dt+sigma*sqrt(dt)*Wiener
        """
    
        x_new = np.array([x_previ - 0.1*x_previ*timestep + sigma * np.sqrt(timestep) * np.random.normal(loc=0.0, scale=np.sqrt(timestep)) for x_previ in x_prev])
        #x_new = np.zero_like(x_prev)
        return x_new

    def W_in(self,n,n_desc,n_asc):


        # Initialize the matrix with zeros
        W = np.zeros((n, n))

        # Populate the matrix according to the given rules
        for i in range(n):
            for j in range(n):
                if i <= j and (j - i) <= n_asc:
                    W[i, j] = 1 / (j - i + 1)
                elif i > j and (i - j) <= n_desc:
                    W[i, j] = 1 / (i - j + 1)
        return W
    def W_mc(self):
        ncm=5
        W=np.zeros((self.n_muscle_cells,self.n_neurons))
        for i in range(self.n_muscle_cells):
            for j in range(self.n_neurons):
                if ncm*i<=j<=ncm*(i+1)-1:
                    W[i,j]=1
        return W


    def step_euler(self, iteration, time, timestep, pos=None):
        """Euler step"""
        self.state[iteration+1, :] = self.state[iteration, :] + \
            timestep*self.f(time, self.state[iteration], pos=pos)
        return np.concatenate([
            self.zeros8,  # the first 4 passive joints
            self.motor_output(iteration),  # the active joints
            self.zeros2  # the last (tail) passive joint
        ])

    def step_euler_maruyama(self, iteration, time, timestep, pos=None):
        """Euler Maruyama step"""
        self.state[iteration+1, :] = self.state[iteration, :] + \
            timestep*self.f(time, self.state[iteration], pos=pos)
        self.noise_vec = self.get_ou_noise_process_dw(
            timestep, self.noise_vec, self.pars.noise_sigma)
        self.state[iteration+1, self.all_v] += self.noise_vec
        self.state[iteration+1,
                   self.all_muscles] = np.maximum(self.state[iteration+1,
                                                             self.all_muscles],
                                                  0)  # prevent from negative muscle activations
        return np.concatenate([
            self.zeros8,  # the first 4 passive joints
            self.motor_output(iteration),  # the active joints
            self.zeros2  # the last (tail) passive joint
        ])

    def motor_output(self, iteration):
        """
        Here you have to final muscle activations for the 10 active joints.
        It should return an array of 2*n_muscle_cells=20 elements,
        even indexes (0,2,4,...) = left muscle activations
        odd indexes (1,3,5,...) = right muscle activations
        """
        array = np.zeros(2 * self.n_muscle_cells)

        for i in range(self.n_muscle_cells):
            array[2*i] = self.state[iteration, self.muscle_l[i]]
            array[2*i+1] = self.state[iteration, self.muscle_r[i]]
        return array    # here you have to final active muscle equations for the 10 joints
    
    def S(self, x):
        return np.sqrt(np.maximum(x,0))
    
    def INTERP(self,x, y ):
        f = CubicSpline(x, y, bc_type='natural')
        return f(self.poses_ext)
    

    def ode_rhs(self,  _time, state, pos=None):
        """Network_ODE
        You should implement here the right hand side of the system of equations
        Parameters
        ----------
        _time: <float>
            Time
        state: <np.array>
            ODE states at time _time
        Returns
        -------
        dstate: <np.array>
            Returns derivative of state
        """
        

        self.dstate[self.L_v] = (-state[self.L_v] + self.S(self.pars.I+self.pars.Idiff-self.pars.b*state[self.L_a]
                                - self.pars.w_inh*np.dot(self.W_in(self.pars.n_neurons,self.pars.n_desc,self.pars.n_asc),state[self.R_v]) 
                                - self.pars.w_stretch*np.dot(self.W_in(self.pars.n_neurons,self.pars.n_desc_str,self.pars.n_asc_str),state[self.R_s]))) / self.pars.tau
        
        self.dstate[self.L_a] = (-state[self.L_a]+self.pars.gamma*state[self.L_v])/self.pars.taua
        
        self.dstate[self.R_v] = (-state[self.R_v] + self.S(self.pars.I-self.pars.Idiff-self.pars.b*state[self.R_a] 
                                - self.pars.w_inh * np.dot(self.W_in(self.pars.n_neurons,self.pars.n_desc,self.pars.n_asc),state[self.L_v])
                                - self.pars.w_stretch * np.dot(self.W_in(self.pars.n_neurons,self.pars.n_desc_str,self.pars.n_asc_str),state[self.L_s]))) / self.pars.tau
        
        self.dstate[self.R_a] = (-state[self.R_a]+self.pars.gamma*state[self.R_v])/self.pars.taua

        self.dstate[self.muscle_l] = self.pars.act_strength*np.dot(self.W_mc(),state[self.L_v])*(1-state[self.muscle_l])/self.pars.taum_a-state[self.muscle_l]/self.pars.taum_d
        self.dstate[self.muscle_r] = self.pars.act_strength*np.dot(self.W_mc(),state[self.R_v])*(1-state[self.muscle_r])/self.pars.taum_a-state[self.muscle_r]/self.pars.taum_d
        
        self.dstate[self.L_s] = (self.S(self.INTERP(self.poses,pos)) * (1-state[self.L_s]) - state[self.L_s])/self.pars.tau_str
        self.dstate[self.R_s] = (self.S(-self.INTERP(self.poses,pos)) * (1-state[self.R_s]) - state[self.R_s])/self.pars.tau_str

        return self.dstate

    def ode_rhs_bis(self,  _time, state, pos=None):
        """Network_ODE
        You should implement here the right hand side of the system of equations
        Parameters
        ----------
        _time: <float>
            Time
        state: <np.array>
            ODE states at time _time
        Returns
        -------
        dstate: <np.array>
            Returns derivative of state
        """
        

        self.dstate[self.L_v] = (-state[self.L_v] + self.S(self.pars.I +self.pars.Idiff -self.pars.b*state[self.L_a]-self.pars.w_inh*np.dot(self.W_in(self.pars.n_neurons,self.pars.n_desc,self.pars.n_asc),state[self.R_v])))/self.pars.tau
        self.dstate[self.L_a] = (-state[self.L_a]+self.pars.gamma*state[self.L_v])/self.pars.taua
        self.dstate[self.R_v] = (-state[self.R_v] + self.S(self.pars.I -self.pars.Idiff -self.pars.b*state[self.R_a]-self.pars.w_inh*np.dot(self.W_in(self.pars.n_neurons,self.pars.n_desc,self.pars.n_asc),state[self.L_v])))/self.pars.tau
        self.dstate[self.R_a] = (-state[self.R_a]+self.pars.gamma*state[self.R_v])/self.pars.taua
        self.dstate[self.muscle_l] = self.pars.act_strength*np.dot(self.W_mc(),state[self.L_v])*(1-state[self.muscle_l])/self.pars.taum_a-state[self.muscle_l]/self.pars.taum_d
        self.dstate[self.muscle_r] = self.pars.act_strength*np.dot(self.W_mc(),state[self.R_v])*(1-state[self.muscle_r])/self.pars.taum_a-state[self.muscle_r]/self.pars.taum_d
        
        self.dstate[self.L_s] = 0
        self.dstate[self.R_s] = 0

        return self.dstate
