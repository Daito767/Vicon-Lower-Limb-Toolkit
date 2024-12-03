# -*- coding: utf-8 -*-
"""
Created on November 2024

@author: Ghimciuc Ioan
"""

import numpy as np
from typing import List

from src.utils.body import Leg
from src.utils.vector_operations import calculate_angles, radians_to_degrees


def get_hip_angles(leg: Leg) -> np.ndarray:
	asi_marker_trajectory = leg.get_marker('ASI').trajectory[leg.strike_event.frames[0]:leg.strike_event.frames[1]]
	psi_marker_trajectory = leg.get_marker('PSI').trajectory[leg.strike_event.frames[0]:leg.strike_event.frames[1]]
	knee_marker_trajectory = leg.get_marker('KNE').trajectory[leg.strike_event.frames[0]:leg.strike_event.frames[1]]
	middle_point_trajectory = (asi_marker_trajectory + psi_marker_trajectory) / 2
	horizontal_normal = np.repeat([[0, 0, 1]], middle_point_trajectory.shape[0], axis=0)

	# Find the scheme of the calculation formula in the src/reports folder in png format
	angles_b = get_angles(knee_marker_trajectory, middle_point_trajectory, asi_marker_trajectory)
	angles_u = radians_to_degrees(calculate_angles(horizontal_normal, asi_marker_trajectory - middle_point_trajectory))
	return 180 - angles_b - angles_u


def get_knee_angles(leg: Leg) -> np.ndarray:
	asi_marker_trajectory = leg.get_marker('ASI').trajectory[leg.strike_event.frames[0]:leg.strike_event.frames[1]]
	psi_marker_trajectory = leg.get_marker('PSI').trajectory[leg.strike_event.frames[0]:leg.strike_event.frames[1]]
	knee_marker_trajectory = leg.get_marker('KNE').trajectory[leg.strike_event.frames[0]:leg.strike_event.frames[1]]
	ank_marker_trajectory = leg.get_marker('ANK').trajectory[leg.strike_event.frames[0]:leg.strike_event.frames[1]]
	middle_trajectory = (asi_marker_trajectory + psi_marker_trajectory) / 2
	angles = get_angles(middle_trajectory, knee_marker_trajectory, ank_marker_trajectory)
	return 180 - angles


def get_foot_angles(leg: Leg) -> np.ndarray:
	knee_marker_trajectory = leg.get_marker('KNE').trajectory[leg.strike_event.frames[0]:leg.strike_event.frames[1]]
	ank_marker_trajectory = leg.get_marker('ANK').trajectory[leg.strike_event.frames[0]:leg.strike_event.frames[1]]
	toe_marker_trajectory = leg.get_marker('TOE').trajectory[leg.strike_event.frames[0]:leg.strike_event.frames[1]]
	angles = get_angles(knee_marker_trajectory, ank_marker_trajectory, toe_marker_trajectory)
	return 90 - angles


def get_angles(marker1_trajectory: np.ndarray, marker2_trajectory: np.ndarray, marker3_trajectory: np.ndarray) -> np.ndarray:
	vector1 = marker1_trajectory - marker2_trajectory
	vector2 = marker3_trajectory - marker2_trajectory
	angle_radians = calculate_angles(vector1, vector2)
	angle_degrees = radians_to_degrees(angle_radians)
	return angle_degrees


def resample_angles(angles: np.ndarray, target_length: int = 100) -> np.ndarray:
	current_length = len(angles)
	original_indices = np.linspace(0, current_length - 1, num=current_length)
	target_indices = np.linspace(0, current_length - 1, num=target_length)
	resampled_angles = np.interp(target_indices, original_indices, angles)
	return resampled_angles


class GaitAnglesReport:
	def __init__(self, left_leg: Leg, right_leg: Leg):
		self.left_hip_angles: List[float] = []
		self.left_knee_angles: List[float] = []
		self.left_foot_angles: List[float] = []
		self.right_hip_angles: List[float] = []
		self.right_knee_angles: List[float] = []
		self.right_foot_angles: List[float] = []
		self._make(left_leg, right_leg)

	def _make(self, left_leg: Leg, right_leg: Leg):
		self.left_hip_angles = resample_angles(get_hip_angles(left_leg)).tolist()
		self.left_knee_angles = resample_angles(get_knee_angles(left_leg)).tolist()
		self.left_foot_angles = resample_angles(get_foot_angles(left_leg)).tolist()

		self.right_hip_angles = resample_angles(get_hip_angles(right_leg)).tolist()
		self.right_knee_angles = resample_angles(get_knee_angles(right_leg)).tolist()
		self.right_foot_angles = resample_angles(get_foot_angles(right_leg)).tolist()
