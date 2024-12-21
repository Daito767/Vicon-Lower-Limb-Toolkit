# -*- coding: utf-8 -*-
"""
Created on June 2024

@author: Ghimciuc Ioan
"""

from typing import List, Dict

import numpy as np
from viconnexusapi import ViconNexus


class Marker:
    def __init__(self, name: str, marker_trajectory: tuple, start_frame: int, end_frame: int):
        self.name: str = name
        self.is_exist_trajectory: List[bool] = marker_trajectory[3][start_frame - 1:end_frame + 1]
        self.trajectory = np.column_stack((marker_trajectory[0][start_frame - 1:end_frame + 1],
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


class Channel:
    def __init__(self, id: int, name: str, ready: bool, rate: int, data: List[int], start_frame: int, end_frame: int, unit: str):
        self.id: int = id
        self.name: str = name
        self.ready: bool = ready
        self.rate: int = rate
        self.start_frame: int = start_frame
        self.end_frame: int = end_frame
        self.data: List[int] = data[start_frame:end_frame + 1]
        self.unit: str = unit

    def __str__(self) -> str:
        return self.name


class Output:
    def __init__(self, id: int, name: str, type: str, unit: str, ready: bool, channels):
        self.id: int = id
        self.name: str = name
        self.type: str = type
        self.unit: str = unit
        self.ready: bool = ready
        self.channels: List[Channel] = channels

    def __str__(self) -> str:
        return self.name


class Device:
    def __init__(self, id: int, name: str, device_type: str, rate: int, outputs: List[Output]):
        self.name: str = name
        self.device_type: str = device_type
        self.rate: float = rate
        self.id: int = id
        self.outputs = outputs

    def __str__(self) -> str:
        return self.name


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

    def GetDevices(self) -> Dict[str, Device]:
        device_ids: List[int] = self.GetDeviceIDs()
        devices: Dict[str, Device] = {}

        for device_id in device_ids:
            device = self.GetDevice(device_id)
            devices[f"{device_id} {device.name}"] = device

        return devices

    def GetDevice(self, device_id: int) -> Device:
        device_name, device_type, device_rate, output_ids, _, _ = self.GetDeviceDetails(device_id)
        device_outputs: List[Output] = [self.GetOutput(output_id, device_id) for output_id in output_ids]
        return Device(device_id, device_name, device_type, device_rate, device_outputs)

    def GetOutput(self, output_id: int, device_id: int) -> Output:
        output_name, output_type, output_unit, output_ready, channel_names, channel_ids = self.GetDeviceOutputDetails(device_id, output_id)
        output_channels: List[Channel] = [self.GetChannel(device_id, output_id, channel_id, channel_name, output_unit) for channel_id, channel_name in zip(channel_ids, channel_names)]
        return Output(output_id, output_name, output_type, output_unit, output_ready, output_channels)

    def GetChannel(self, device_id: int, output_id: int, channel_id: int, channel_name: str, unit: str = 'Unknown') -> Channel:
        start_frame, end_frame = self.GetTrialRegionOfInterest()
        channel_data, channel_ready, channel_rate = self.GetDeviceChannel(device_id, output_id, channel_id)

        recording_rate = self.GetFrameRate()
        start_index = int(start_frame * channel_rate / recording_rate)
        end_index = int(end_frame * channel_rate / recording_rate)

        return Channel(channel_id, channel_name, channel_ready, channel_rate, channel_data, start_index, end_index, unit)
