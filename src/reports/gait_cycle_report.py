# -*- coding: utf-8 -*-
"""
Created on November 2024

@author: Ghimciuc Ioan
"""
from typing import Dict

from src.utils.body import Leg


def get_phases_percentage_duration(cycle_phases: Dict[str, int], leg: Leg, total_frame_duration: int) -> Dict[str, float]:
	k = 100 / total_frame_duration
	phases_percentage_duration = {"Bipodal 1": (cycle_phases["Monopodal"] - leg.strike_event.frames[0]) * k,
								  "Monopodal": (cycle_phases["Bipodal"] - cycle_phases["Monopodal"]) * k,
								  "Bipodal 2": (cycle_phases["Balance"] - cycle_phases["Bipodal"]) * k,
								  "Balance": (leg.strike_event.frames[1] - cycle_phases["Balance"]) * k}
	return phases_percentage_duration


def get_cycle_phases(primary_leg: Leg, secondary_leg: Leg, is_primary_leg_first: bool) -> Dict[str, int]:
	cycle_phases: Dict[str, int] = {"Monopodal": primary_leg.off_event.frames[0]}

	if is_primary_leg_first:
		cycle_phases["Bipodal"] = secondary_leg.strike_event.frames[0]
		cycle_phases["Balance"] = secondary_leg.off_event.frames[0]
	else:
		cycle_phases["Bipodal"] = secondary_leg.strike_event.frames[1]
		cycle_phases["Balance"] = secondary_leg.off_event.frames[1]

	return cycle_phases


class GaitCycleReport:
	def __init__(self, left_leg: Leg, right_leg: Leg):
		self.left_total_frame_duration = 0
		self.right_total_frame_duration = 0
		self.left_cycle_phases: Dict[str, int] = {}
		self.right_cycle_phases: Dict[str, int] = {}
		self.left_phases_percentage_duration: Dict[str, float] = {}
		self.right_phases_percentage_duration: Dict[str, float] = {}
		self._make(left_leg, right_leg)

	def _make(self, left_leg: Leg, right_leg: Leg):
		is_left_foot_first = True
		if left_leg.strike_event.frames[0] > right_leg.strike_event.frames[0]:
			is_left_foot_first = False

		self.left_total_frame_duration = left_leg.strike_event.frames[1] - left_leg.strike_event.frames[0]
		self.right_total_frame_duration = right_leg.strike_event.frames[1] - right_leg.strike_event.frames[0]
		self.left_cycle_phases = get_cycle_phases(left_leg, right_leg, is_left_foot_first)
		self.right_cycle_phases = get_cycle_phases(right_leg, left_leg, not is_left_foot_first)
		self.left_phases_percentage_duration = get_phases_percentage_duration(self.left_cycle_phases, left_leg, self.left_total_frame_duration)
		self.right_phases_percentage_duration = get_phases_percentage_duration(self.right_cycle_phases, right_leg, self.right_total_frame_duration)
