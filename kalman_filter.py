import numpy as np


class KalmanFilter(object):
    def __init__(self, state_transition=None, control_input=None, observation=None,
                 process_noise=None, observation_noise=None, covariance=None, state=None):
        if state_transition is None or observation is None:
            raise ValueError

        self.n = state_transition.shape[1]
        self.m = observation.shape[1]

        self.F = state_transition
        self.H = observation
        self.B = 0 if (control_input is None) else control_input
        self.Q = np.eye(self.n) if (process_noise is None) else process_noise
        self.R = np.eye(self.n) if (observation_noise is None) else observation_noise
        self.P = np.eye(self.n) if (covariance is None) else covariance
        self.x = np.zeros((self.n, 1)) if (state is None) else state

    def predict(self, control_vector=0):
        # Predict state estimate
        self.x = np.dot(self.F, self.x) + np.dot(self.B, control_vector)
        # Predict covariance
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q
        return self.x

    def update(self, mean):
        pre_fit_covariance = self.R + np.dot(self.H, np.dot(self.P, self.H.T))
        kalman_gain = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(pre_fit_covariance))
        # Update state estimate
        self.x = self.x + np.dot(kalman_gain, mean - np.dot(self.H, self.x))
        # Update covariance
        self.P = np.dot(np.dot(np.eye(self.n) - np.dot(kalman_gain, self.H), self.P),
                        (np.eye(self.n) - np.dot(kalman_gain, self.H)).T) + np.dot(np.dot(kalman_gain, self.R),
                                                                                   kalman_gain.T)
