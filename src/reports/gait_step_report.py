# -*- coding: utf-8 -*-
"""
Created on November 2024

@author: Ghimciuc Ioan
"""

import numpy as np
from src.utils.body import Leg


def calculate_step_length(foot1: Leg, foot2: Leg, is_foot1_first: bool) -> float:
	start_frame_position = foot1.get_marker('HEE').trajectory[foot1.strike_event.frames[0]]
	end_frame_position = foot2.get_marker('HEE').trajectory[foot2.strike_event.frames[is_foot1_first]]
	return np.linalg.norm(end_frame_position - start_frame_position)


def calculate_step_height(foot: Leg) -> float:
	y_positions = foot.get_marker('ANK').trajectory[foot.strike_event.frames[0]:foot.strike_event.frames[1], 2]
	return max(y_positions) - min(y_positions)


def calculate_step_frame_duration(foot1: Leg, foot2: Leg, is_foot1_first: bool) -> int:
	return abs(foot1.strike_event.frames[not is_foot1_first] - foot2.strike_event.frames[not is_foot1_first])


class GaitStepReport:
	def __init__(self, left_leg: Leg, right_leg: Leg, frame_rate: int):
		self.left_step_speed: float = 0
		self.right_step_speed: float = 0
		self.left_step_height: float = 0
		self.right_step_height: float = 0
		self.left_step_length: float = 0
		self.right_step_length: float = 0
		self.left_step_cadence: float = 0
		self.right_step_cadence: float = 0
		self.left_step_frames_duration: int = 0
		self.right_step_frames_duration: int = 0
		self._make(left_leg, right_leg, frame_rate)

	def _make(self, left_leg: Leg, right_leg: Leg, frame_rate: int):
		is_left_foot_first = True
		if left_leg.strike_event.frames[0] > right_leg.strike_event.frames[0]:
			is_left_foot_first = False

		self.left_step_height = calculate_step_height(left_leg)
		self.right_step_height = calculate_step_height(right_leg)
		self.left_step_length = calculate_step_length(right_leg, left_leg, is_foot1_first=is_left_foot_first)
		self.right_step_length = calculate_step_length(left_leg, right_leg, is_foot1_first=not is_left_foot_first)
		self.left_step_frames_duration = calculate_step_frame_duration(left_leg, right_leg, is_foot1_first=is_left_foot_first)
		self.right_step_frames_duration = calculate_step_frame_duration(right_leg, left_leg, is_foot1_first=not is_left_foot_first)

		self.left_step_speed = (self.left_step_length / self.left_step_frames_duration) * frame_rate
		self.right_step_speed = (self.right_step_length / self.right_step_frames_duration) * frame_rate
		self.left_step_cadence = (60 * frame_rate) / self.left_step_frames_duration
		self.right_step_cadence = (60 * frame_rate) / self.right_step_frames_duration
