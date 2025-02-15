#!/usr/bin/env python
from __future__ import division
from threading import Lock
import numpy as np
from numpy.core.numeric import roll
import rospy
import math

from std_msgs.msg import Float64

import matplotlib.pyplot as plt


class KinematicCarMotionModel:
    """The kinematic car motion model."""

    def __init__(self, car_length, **kwargs):
        """Initialize the kinematic car motion model.

        Args:
            car_length: the length of the car
            **kwargs (object): any number of optional keyword arguments:
                vel_std (float): std dev of the control velocity noise
                alpha_std (float): std dev of the control alpha noise
                x_std (float): std dev of the x position noise
                y_std (float): std dev of the y position noise
                theta_std (float): std dev of the theta noise
        """

        defaults = {
            "vel_std": 0.1,
            "alpha_std": 0.1,
            "x_std": 0.05,
            "y_std": 0.05,
            "theta_std": 0.1,
        }
        if not set(kwargs).issubset(set(defaults)):
            raise ValueError("Invalid keyword argument provided")
        # These next two lines set the instance attributes from the defaults and
        # kwargs dictionaries. For example, the key "vel_std" becomes the
        # instance attribute self.vel_std.
        self.__dict__.update(defaults)
        self.__dict__.update(kwargs)

        if car_length <= 0.0:
            raise ValueError(
                "The model is only defined for defined for positive, non-zero car lengths"
            )
        self.car_length = car_length

    def compute_changes(self, states, controls, dt, alpha_threshold=1e-2):
        """Integrate the (deterministic) kinematic car model.

        Given vectorized states and controls, compute the changes in state when
        applying the control for duration dt.

        If the absolute value of the applied alpha is below alpha_threshold,
        round down to 0. We assume that the steering angle (and therefore the
        orientation component of state) does not change in this case.

        Args:
            states: np.array of states with shape M x 3
            states = [x, y, theta]
            controls: np.array of controls with shape M x 2
            controls = [velocity, alpha]
            dt (float): control duration

        Returns:
            M x 3 np.array, where the three columns are dx, dy, dtheta

        """
        # BEGIN "QUESTION 1.2" ALT="return np.zeros_like(states, dtype=float)"
        dx = []
        dy = []
        dtheta = []
        change_array = []
        for i in range(len(states)):
            x = states[i][0]
            y = states[i][1]
            theta = states[i][2]
            vel = controls[i][0]
            alpha = controls[i][1]

            if(abs(alpha) >= abs(alpha_threshold) ):
                dtheta.append((vel/self.car_length) * np.tan(alpha) * dt)
                dx.append((self.car_length/np.tan(alpha))*(np.sin(theta + dtheta[i])-np.sin(theta)))
                dy.append((self.car_length/np.tan(alpha))*(np.cos(theta)-np.cos(theta + dtheta[i])))

            else:
                dtheta.append(0)
                dx.append(vel*np.cos(theta)*dt)
                dy.append(vel*np.sin(theta)*dt)


            
            change_array.append([dx[i],dy[i],dtheta[i]])

        return np.array(change_array)
        # END

    def apply_deterministic_motion_model(self, states, vel, alpha, dt):
        """Propagate states through the determistic kinematic car motion model.

        Given the nominal control (vel, alpha
        ), compute the changes in state 
        and update it to the resulting state.

        NOTE: This function does not have a return value: your implementation
        should modify the states argument in-place with the updated states.

        >>> states = np.ones((3, 2))
        >>> states[2, :] = np.arange(2)  #  modifies the row at index 2
        >>> a = np.array([[1, 2], [3, 4], [5, 6]])
        >>> states[:] = a + a            # modifies states; note the [:]

        Args:
            states: np.array of states with shape M x 3
            vel (float): nominal control velocity
            alpha (float): nominal control steering angle
            dt (float): control duration
        """
        n_particles = states.shape[0]

        # Hint: use same controls for all the particles
        # BEGIN SOLUTION "QUESTION 1.3"
        controls = np.ones((len(states),2))
        controls[:,0] = vel
        controls[:,1] = alpha
        change_array = self.compute_changes(states, controls, dt)
        for i in range(len(states)):
            states[i, :] += [change_array[i][0], change_array[i][1], change_array[i][2]]
            states[i][2] = states[i][2] % (2 * np.pi)
            if(states[i][2] > np.pi):
                states[i][2] = states[i][2] - (2*np.pi)
        # END SOLUTION

    def apply_motion_model(self, states, vel, alpha, dt):
        """Propagate states through the noisy kinematic car motion model.

        Given the nominal control (vel, alpha), sample M noisy controls.
        Then, compute the changes in state with the noisy controls.
        Finally, add noise to the resulting states.

        NOTE: This function does not have a return value: your implementation
        should modify the states argument in-place with the updated states.

        >>> states = np.ones((3, 2))
        >>> states[2, :] = np.arange(2)  #  modifies the row at index 2
        >>> a = np.array([[1, 2], [3, 4], [5, 6]])
        >>> states[:] = a + a            # modifies states; note the [:]

        Args:
            states: np.array of states with shape M x 3
            vel (float): nominal control velocity
            alpha (float): nominal control steering angle
            dt (float): control duration
        """
        n_particles = states.shape[0]

        # Hint: you may find the np.random.normal function useful
        # BEGIN SOLUTION "QUESTION 1.4"
        controls = np.ones((len(states),2))

        v = np.random.normal(vel,self.vel_std,(n_particles,1))
        a= np.random.normal(alpha,self.alpha_std,(n_particles,1))
        
        dstates = self.compute_changes(states, np.column_stack((v, a)), dt)

        states[:,0] = states[:,0] + np.random.normal(dstates[:,0], self.x_std, (1,n_particles))
        states[:,1] = states[:,1] + np.random.normal(dstates[:,1], self.y_std, (1,n_particles))
        states[:,2] = states[:,2] + np.random.normal(dstates[:,2], self.theta_std, (1,n_particles))

        for i in range(len(states)):
            states[i][2] = states[i][2] % (2 * np.pi)
            if(states[i][2] > np.pi):
                states[i][2] = states[i][2] - (2*np.pi)
        # END SOLUTION
