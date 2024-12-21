# -*- coding: utf-8 -*-
"""
Created on December 2024

@author: Ghimciuc Ioan
"""

import os
from typing import List

import numpy as np
from fpdf import FPDF, XPos, YPos
from matplotlib import pyplot as plt
from src.reports.gait_angles_report import get_knee_angles, get_hip_angles, get_foot_angles
from src.reports.motion_report import MotionReport
from src.utils.body import Leg
from src.utils.vicon_nexus import Event, Channel

REFERENCE_PHASES_PERCENT = [12, 50, 62]


def add_channel_plots(channels: List[Channel], output_directory: str, start_frame: int, end_frame: int, phases: List[int], vicon_frame_rate: int, phase_duration: int) -> List[str]:
	"""Generate plots for EMG channels with gait phases."""
	image_paths = []
	for i in range(0, len(channels), 8):
		fig, axs = plt.subplots(8, 1, figsize=(10, 14))
		for j, channel in enumerate(channels[i:i + 8]):
			# Map camera frames to EMG frame indices
			start_index = int(start_frame * channel.rate / vicon_frame_rate)
			end_index = int(end_frame * channel.rate / vicon_frame_rate)
			data = channel.data[start_index:end_index + 1]

			# Plot the channel data
			axs[j].plot(data, label=channel.name, color='deepskyblue')
			axs[j].set_title(channel.name)
			axs[j].set_xlabel("Ciclul de mers (cadre EMG)")
			axs[j].set_ylabel(channel.unit)
			axs[j].grid(False)

			# Convert gait phases to EMG frames
			emg_phases = [int((phase - start_frame) * len(data) / phase_duration) for phase in phases]
			reference_emg_phases = [int(percent / 100 * len(data)) for percent in REFERENCE_PHASES_PERCENT]

			# Draw vertical lines for gait phases
			for phase in emg_phases:
				axs[j].axvline(x=phase, color='blue', linestyle='solid', linewidth=1)

			for ref_phase in reference_emg_phases:
				axs[j].axvline(x=ref_phase, color='orange', linestyle='dashed', linewidth=1.5)

		# Remove unused subplots
		for k in range(len(channels[i:i + 8]), 8):
			fig.delaxes(axs[k])

		plt.tight_layout()
		# start_frame and end_frame ensure the uniqueness of the name of the image, otherwise the pdf will show the same photo
		image_path = os.path.join(output_directory, f"{start_frame} {end_frame} channels_page_{i // 8 + 1}.png")
		plt.savefig(image_path)
		plt.close(fig)
		image_paths.append(image_path)

	return image_paths


def process_channels(report: MotionReport, output_directory: str, leg: Leg, phase_duration: int, leg_phases: List[int], title: str, pdf: FPDF):
	channels = []
	for device in report.devices.values():
		for output in device.outputs:
			channels.extend(output.channels)

	channel_images = add_channel_plots(
		channels=channels,
		output_directory=output_directory,
		start_frame=leg.strike_event.frames[0],
		end_frame=leg.strike_event.frames[1],
		phases=leg_phases,
		vicon_frame_rate=report.frame_rate,
		phase_duration=phase_duration,
	)

	# Add images to the PDF
	for image_path in channel_images:
		pdf.add_page()
		pdf.cell(0, 0, title, new_x=XPos.LMARGIN, new_y=YPos.TOP, align="C")
		pdf.image(image_path, x=0, y=15, w=200)
		os.remove(image_path)


def _add_channels(report: MotionReport, pdf: FPDF, output_directory: str):
	process_channels(
		report=report,
		output_directory=output_directory,
		leg=report.left_leg,
		leg_phases=list(report.gait_cycle_report.left_cycle_phases.values()),
		phase_duration=report.gait_cycle_report.left_total_frame_duration,
		title="Membrul inferior stâng",
		pdf=pdf
	)

	process_channels(
		report=report,
		output_directory=output_directory,
		leg=report.right_leg,
		leg_phases=list(report.gait_cycle_report.right_cycle_phases.values()),
		phase_duration=report.gait_cycle_report.right_total_frame_duration,
		title="Membrul inferior drept",
		pdf=pdf
	)


def export_plot_leg_angles(angles: dict, reference_angles: dict, phases: List[int], title_prefix: str, output_path: str) -> None:
	"""Generates a plot with knee, foot, and hip angles for a specific leg, overlaying real and reference angles."""
	fig, axs = plt.subplots(3, 1, figsize=(10, 14))

	axs[0].plot(angles["hip"], label="Măsurat", color='blue')
	axs[0].plot(reference_angles["hip"], label="Etalon", linestyle="--", color='orange')
	axs[0].set_title(f"Variația amplitudinii unghiului șoldului")
	axs[0].set_xlabel("Ciclul de mers (procente)")
	axs[0].set_ylabel("Unghi (grade)")
	axs[0].legend()
	axs[0].grid(False)

	axs[1].plot(angles["knee"], label="Măsurat", color='blue')
	axs[1].plot(reference_angles["knee"], label="Etalon", linestyle="--", color='orange')
	axs[1].set_title(f"Variația amplitudinii unghiului genunchiului")
	axs[1].set_xlabel("Ciclul de mers (procente)")
	axs[1].set_ylabel("Unghi (grade)")
	axs[1].legend()
	axs[1].grid(False)

	axs[2].plot(angles["foot"], label="Măsurat", color='blue')
	axs[2].plot(reference_angles["foot"], label="Etalon", linestyle="--", color='orange')
	axs[2].set_title(f"Variația amplitudinii unghiului gleznei")
	axs[2].set_xlabel("Ciclul de mers (procente)")
	axs[2].set_ylabel("Unghi (grade)")
	axs[2].legend()
	axs[2].grid(False)

	rounded_phases = [round(phase) for phase in phases if phase]
	xticks = [x for x in range(0, 101, 5) if all(abs(x - phase) >= 3 for phase in rounded_phases)]

	for ax in axs:
		ax.set_xticks(xticks + rounded_phases)
		for phase in phases:
			ax.axvline(x=phase, color='blue', linestyle='solid', linewidth=1)
		for phase in REFERENCE_PHASES_PERCENT:
			ax.axvline(x=phase, color='orange', linestyle='dashed', linewidth=1.5, dashes=(5, 7))

	plt.tight_layout()
	plt.savefig(output_path)
	plt.close(fig)


def _add_angles(report: MotionReport, pdf: FPDF, output_directory: str):
	left_leg_angles = {
		"knee": report.gait_angles_report.left_knee_angles,
		"foot": report.gait_angles_report.left_foot_angles,
		"hip": report.gait_angles_report.left_hip_angles,
	}
	right_leg_angles = {
		"knee": report.gait_angles_report.right_knee_angles,
		"foot": report.gait_angles_report.right_foot_angles,
		"hip": report.gait_angles_report.right_hip_angles,
	}
	reference_angles = {
		"knee": report.reference_knee_angles,
		"foot": report.reference_foot_angles,
		"hip": report.reference_hip_angles,
	}

	left_k = 100 / report.gait_cycle_report.left_total_frame_duration
	right_k = 100 / report.gait_cycle_report.right_total_frame_duration
	left_phases: List[int] = [(phase - report.left_leg.strike_event.frames[0]) * left_k for phase in report.gait_cycle_report.left_cycle_phases.values()]
	right_phases: List[int] = [(phase - report.right_leg.strike_event.frames[0]) * right_k for phase in report.gait_cycle_report.right_cycle_phases.values()]

	pdf.add_page()
	left_chart_path = os.path.join(output_directory, "left_leg_angles.png")
	export_plot_leg_angles(left_leg_angles, reference_angles, left_phases, "Left Leg", left_chart_path)
	pdf.cell(0, 0, f"Analiza unghiurilor membrului inferior stâng", new_x=XPos.LMARGIN, new_y=YPos.TOP, align="C")
	pdf.image(left_chart_path, x=0, y=15, w=200)

	pdf.add_page()
	right_chart_path = os.path.join(output_directory, "right_leg_angles.png")
	export_plot_leg_angles(right_leg_angles, reference_angles, right_phases, "Right Leg", right_chart_path)
	pdf.cell(0, 0, f"Analiza unghiurilor membrului inferior drept", new_x=XPos.LMARGIN, new_y=YPos.TOP, align="C")
	pdf.image(right_chart_path, x=0, y=15, w=200)

	os.remove(left_chart_path)
	os.remove(right_chart_path)


def export(report: MotionReport, report_name: str, output_directory: str, export_channels: bool = False) -> None:
	pdf = FPDF()
	pdf.set_auto_page_break(auto=True, margin=5)
	pdf.set_font("Helvetica", "B", 16)

	_add_angles(report, pdf, output_directory)

	if export_channels:
		_add_channels(report, pdf, output_directory)

	pdf_output_path = os.path.join(output_directory, f"{report_name}.pdf")
	pdf.output(pdf_output_path)
