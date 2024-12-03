# -*- coding: utf-8 -*-
"""
Created on November 2024

@author: Ghimciuc Ioan
"""
from typing import Dict

from src.utils.vicon_nexus import Marker, Event


class Leg:
	def __init__(self, side: chr, markers: Dict[str, Marker], strike_event: Event, off_event: Event):
		self.side = side.upper()
		self.markers = markers
		self.strike_event = strike_event
		self.off_event = off_event

	def get_marker(self, name: str) -> Marker:
		return self.markers[self.side + name.upper()]

	def __str__(self):
		return f'{self.side} Foot'
