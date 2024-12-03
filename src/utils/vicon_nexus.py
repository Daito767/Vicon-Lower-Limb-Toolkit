# -*- coding: utf-8 -*-
"""
Created on June 2024

@author: Ghimciuc Ioan
"""
from typing import List, Dict
from viconnexusapi import ViconNexus
import numpy


class Marker:
    def __init__(self, name: str, marker_trajectory: tuple, start_frame: int, end_frame: int):
        self.name: str = name
        self.is_exist_trajectory: List[bool] = marker_trajectory[3]
        self.trajectory = numpy.column_stack((marker_trajectory[0][start_frame - 1:end_frame + 1],
                                             marker_trajectory[1][start_frame - 1:end_frame + 1],
                                             marker_trajectory[2][start_frame - 1:end_frame + 1]))

    def __str__(self) -> str:
        return self.name


class Event:
    def __init__(self, context: str, event_name: str, frames: List[int], offsets: List[float]):
        self.name: str = event_name
        self.context: str = context
        self.frames: List[int] = frames
        self.offsets: List[float] = offsets

    def __str__(self) -> str:
        return f'{self.context} {self.name}'


class ViconNexusAPI(ViconNexus.ViconNexus):
    def __init__(self, host='localhost'):
        super().__init__(host)

    def GetMarkers(self, subject_name: str) -> Dict[str, Marker]:
        start_frame, end_frame = self.GetTrialRegionOfInterest()
        markers: Dict[str, Marker] = {}

        for marker_name in self.GetMarkerNames(subject_name):
            marker_trajectory = self.GetTrajectory(subject_name, marker_name)
            markers[marker_name] = Marker(marker_name, marker_trajectory, start_frame, end_frame)

        return markers

    def GetEvent(self, subject_name: str, context: str, event: str) -> Event:
        events: List[List[int], List[float]] = self.GetEvents(subject_name, context, event)
        return Event(context, event, events[0], events[1])
