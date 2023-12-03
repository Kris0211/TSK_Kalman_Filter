import numpy as np


class EzKalmanFilter:

    def __init__(
            self,
            start_position: np.ndarray,
            start_velocity: np.ndarray,
            observation_noise: float,
            prediction_noise: float):

        self.state = np.array([
            start_position[0],
            start_velocity[0],
            start_position[1],
            start_velocity[1]]).T

        self.observation_model = np.array([
            [1, 0, 0, 0],
            [0, 0, 1, 0]
        ])

        self.observation_noise = np.array([
            [1, 0],
            [0, 1]
        ]) * (observation_noise ** 2)

        self.estimate_covariance = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        self.prediction_noise = np.array([
            [0, 1, 0, 0],
            [1, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 1]
        ]) * prediction_noise

    def _get_state_transition(self, delta_time: float):
        return np.array([
            [1, delta_time, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, delta_time],
            [0, 0, 0, 1]
        ])

    def predict(self, delta_time: float, velocity: np.ndarray):
        f = self._get_state_transition(delta_time)
        self.state[1] = velocity[0]
        self.state[3] = velocity[1]
        self.state = np.matmul(f, self.state)
        self.estimate_covariance = np.matmul(f, self.prediction_noise)
        self.estimate_covariance = np.matmul(self.estimate_covariance, f.T)
        self.estimate_covariance += self.prediction_noise

        return self.state, self.estimate_covariance

    def update(self, observation: np.ndarray, delta_time: float):
        kalman_gain = np.matmul(self.observation_model, self.estimate_covariance)
        kalman_gain = np.matmul(kalman_gain, self.observation_model.T)
        kalman_gain += self.observation_noise
        kalman_gain = np.matmul(np.matmul(self.estimate_covariance, self.observation_model.T), np.linalg.inv(kalman_gain))

        self.estimate_covariance = self.estimate_covariance - np.matmul(np.matmul(kalman_gain, self.observation_model),
                                                                        self.estimate_covariance)
        observation_delta = observation - np.matmul(self.observation_model, self.state)
        self.state = self.state + np.matmul(kalman_gain, observation_delta)
        return


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

    def update(self, observation_mean):
        pre_fit_covariance = self.R + np.dot(self.H, np.dot(self.P, self.H.T))
        kalman_gain = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(pre_fit_covariance))
        # Update state estimate
        self.x = self.x + np.dot(kalman_gain, observation_mean - np.dot(self.H, self.x))
        # Update covariance
        self.P = np.dot(np.dot(np.eye(self.n) - np.dot(kalman_gain, self.H), self.P),
                        (np.eye(self.n) - np.dot(kalman_gain, self.H)).T) + np.dot(np.dot(kalman_gain, self.R),
                                                                                   kalman_gain.T)
