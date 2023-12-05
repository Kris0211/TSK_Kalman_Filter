import numpy as np


class KalmanFilter(object):
    def __init__(self, position: np.ndarray, velocity: np.ndarray,
                 prediction_noise: float, observation_noise: float, dt: float):

        self.state = np.array([
            position[0],
            velocity[0],
            position[1],
            velocity[1]]
        ).T

        self.observation = np.array([
            [1, 0, 0, 0],
            [0, 0, 1, 0]
        ])

        self.transition_mat = np.array([
            [1, dt, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, dt],
            [0, 0, 0, 1]
        ])

        self.prediction_noise = np.array([
            [0, 1, 0, 0],
            [1, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 1]
        ]) * prediction_noise

        self.observation_noise = np.array([
            [1, 0],
            [0, 1]
        ]) * (observation_noise ** 2)

        self.covariance = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

    def predict(self, dt, velocity):
        # Predict state
        self.state[1] = velocity[0]
        self.state[3] = velocity[1]
        self.state = np.dot(self.transition_mat, self.state)
        # Predict covariance
        self.covariance = np.dot(np.dot(self.transition_mat, self.prediction_noise), self.transition_mat.T)
        self.covariance += self.prediction_noise
        return self.state

    def update(self, observation):
        pre_fit_covariance = self.observation_noise + np.dot(self.observation,
                                                             np.dot(self.covariance, self.observation.T))
        kalman_gain = np.dot(np.dot(self.covariance, self.observation.T), np.linalg.inv(pre_fit_covariance))
        # Update state
        self.state = self.state + np.dot(kalman_gain, observation - np.dot(self.observation, self.state))
        # Update covariance
        self.covariance = self.covariance - np.dot(np.dot(kalman_gain, self.observation), self.covariance)
        observation_delta = observation - np.dot(self.observation, self.state)
        self.state += np.dot(kalman_gain, observation_delta)
