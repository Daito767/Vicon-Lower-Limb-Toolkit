# -*- coding: utf-8 -*-
"""
Created on November 2024

@author: Ghimciuc Ioan
"""


import openpyxl
from typing import List, Dict, Tuple

from src.utils.body import Leg
from src.reports.gait_angles_report import GaitAnglesReport
from src.reports.gait_cycle_report import GaitCycleReport
from src.reports.gait_step_report import GaitStepReport
from src.utils.vicon_nexus import ViconNexusAPI, Marker, Event


def get_reference_angles(xlsx_file_path: str) -> Tuple[List[float], List[float], List[float]]:
	workbook = openpyxl.load_workbook(xlsx_file_path, read_only=True)
	worksheet = workbook.active

	knee_angles: List[float] = []
	foot_angles: List[float] = []
	hip_angles: List[float] = []

	for row in worksheet.iter_rows(min_row=2, values_only=True):
		foot_angles.append(row[1])
		knee_angles.append(row[2])
		hip_angles.append(row[4])

	return knee_angles, foot_angles, hip_angles


def sort_by_side(markers: Dict[str, Marker]) -> Tuple[Dict[str, Marker], Dict[str, Marker]]:
	left_markers, right_markers = {}, {}
	for name, marker in markers.items():
		if name.lower().startswith('l'):
			left_markers[name] = marker
		elif name.lower().startswith('r'):
			right_markers[name] = marker

	return left_markers, right_markers


class MotionReport:
	def __init__(self, vicon: ViconNexusAPI, subject_name: str, reference_angles_file_path: str):
		self.vicon = vicon
		self.subject_name = subject_name
		self.reference_angles_file_path = reference_angles_file_path
		self.frame_rate: int = 0
		self.start_frame: int = 0
		self.end_frame: int = 0
		self.events: Dict[str, Event] = {}
		self.markers: Dict[str, Marker] = {}
		self.reference_knee_angles: List[float] = []
		self.reference_foot_angles: List[float] = []
		self.reference_hip_angles: List[float] = []
		self.left_leg: Leg = None
		self.right_leg: Leg = None
		self.gait_step_report: GaitStepReport = None
		self.gait_cycle_report: GaitCycleReport = None
		self.gait_angles_report: GaitAnglesReport = None
		self._make()

	def _make(self) -> None:
		self._check_if_subject_exists()
		self.frame_rate = self.vicon.GetFrameRate()
		self.start_frame, self.end_frame = self.vicon.GetTrialRegionOfInterest()
		self.events = self._get_events()
		self.markers = self.vicon.GetMarkers(self.subject_name)
		self.reference_knee_angles, self.reference_foot_angles, self.reference_hip_angles = get_reference_angles(self.reference_angles_file_path)

		left_markers, right_markers = sort_by_side(self.markers)
		self.left_leg = Leg('L', left_markers, self.events['Left Foot Strike'], self.events['Left Foot Off'])
		self.right_leg = Leg('R', right_markers, self.events['Right Foot Strike'], self.events['Right Foot Off'])

		self.gait_step_report = GaitStepReport(self.left_leg, self.right_leg, self.frame_rate)
		self.gait_cycle_report = GaitCycleReport(self.left_leg, self.right_leg)
		self.gait_angles_report = GaitAnglesReport(self.left_leg, self.right_leg)

	def _check_if_subject_exists(self) -> None:
		subject_names = self.vicon.GetSubjectNames()
		if self.subject_name not in subject_names:
			raise ValueError(f'Subject name "{self.subject_name}" not in Vicon Nexus')

	def _get_events(self) -> Dict[str, Event]:
		events: Dict[str, Event] = {'Left Foot Strike': self._get_event(self.subject_name, 'Left', 'Foot Strike'),
									'Left Foot Off': self._get_event(self.subject_name, 'Left', 'Foot Off'),
									'Right Foot Strike': self._get_event(self.subject_name, 'Right', 'Foot Strike'),
									'Right Foot Off': self._get_event(self.subject_name, 'Right', 'Foot Off')}
		return events

	def _get_event(self, subject_name: str, context: str, event: str) -> Event:
		event: Event = self.vicon.GetEvent(subject_name, context, event)

		if not event.frames:
			raise ValueError(f'The trial does not contain a "{context} {event}". Please return to Nexus and add one.')

		for i in range(len(event.frames)):
			if event.frames[i] < self.start_frame or event.frames[i] > self.end_frame:
				raise ValueError(f'The "{context} {event}" event frame ({event.frames[i]}) is out of the trial region of interest. '
								 f'Expected frame within range {self.start_frame} to {self.end_frame}. Please check and correct the event frame in Nexus.')

			event.frames[i] -= self.start_frame

		return event


if __name__ == '__main__':
	from src.exporters import motion_report_exporter
	vicon: ViconNexusAPI = ViconNexusAPI()
	subject_names: List[str] = vicon.GetSubjectNames()
	motion_report: MotionReport = MotionReport(vicon, subject_names[0], '../exports/Unghiurile_Perry.xlsx')
	motion_report_exporter.export_pdf(motion_report, 'Report exemple', output_directory='../exports/')
	motion_report_exporter.export_xlsx(motion_report, 'Report exemple', output_directory='../exports/')
