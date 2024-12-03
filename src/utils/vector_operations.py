# -*- coding: utf-8 -*-
"""
Created on June 2024

@author: Ghimciuc Ioan
"""

import numpy as np


def calculate_angles(vectors1: np.ndarray, vectors2: np.ndarray) -> np.ndarray:
	"""
	Returnează unghiurile în radiani dintre vectorii corespunzători din două liste de vectori.

	Parameters:
	vectors1 (np.ndarray): Prima listă de vectori.
	vectors2 (np.ndarray): A doua listă de vectori.

	Returns:
	np.ndarray: Lista cu unghiurile în radiani dintre vectorii corespunzători.
	"""
	vectors1 = np.array(vectors1)
	vectors2 = np.array(vectors2)

	dot_products = np.einsum('ij,ij->i', vectors1, vectors2)  # Calculate dot products

	norms_a = np.linalg.norm(vectors1, axis=1)  # Calculate norms of vectors_a
	norms_b = np.linalg.norm(vectors2, axis=1)  # Calculate norms of vectors_b

	cos_angles = dot_products / (norms_a * norms_b)  # Calculate cosines of angles
	cos_angles = np.clip(cos_angles, -1.0, 1.0)  # Clip values to avoid numerical errors

	angles = np.arccos(cos_angles)  # Calculate angles in radians

	return angles


def radians_to_degrees(angles: np.ndarray) -> np.ndarray:
	"""
		Returnează unghiurile în grade.

		Parameters:
		angles (np.ndarray): Lista cu unghiurile în radiani.

		Returns:
		np.ndarray: Lista cu unghiurile în grade.
		"""
	return np.degrees(angles)


def add_vectors(vectors1: np.ndarray, vectors2: np.ndarray) -> np.ndarray:
	"""
	Returnează suma a două liste de vectori.

	Parameters:
	vectors1 (np.ndarray): Prima listă de vectori.
	vectors2 (np.ndarray): A doua listă de vectori.

	Returns:
	np.ndarray: Lista cu sumele vectorilor corespunzători.
	"""
	return vectors1 + vectors2


def subtract_vectors(vectors1: np.ndarray, vectors2: np.ndarray) -> np.ndarray:
	"""
	Returnează diferența dintre două arrays de vectori.

	Parameters:
	vectors1 (np.ndarray): Prima listă de vectori.
	vectors2 (np.ndarray): A doua listă de vectori.

	Returns:
	np.ndarray: Lista cu diferențele vectorilor corespunzători. (vectors1 - vectors2)
	"""
	return vectors1 - vectors2


def dot_product_vectors(vectors1: np.ndarray, vectors2: np.ndarray) -> np.ndarray:
	"""
	Returnează produsul scalar al vectorilor corespunzători din două arrays.

	Parameters:
	vectors1 (np.ndarray): Prima listă de vectori.
	vectors2 (np.ndarray): A doua listă de vectori.

	Returns:
	np.ndarray: Lista cu produsele scalare ale vectorilor corespunzători.
	"""
	return np.einsum('ij,ij->i', vectors1, vectors2)


def norms_of_vectors(vectors: np.ndarray) -> np.ndarray:
	"""
	Returnează normele (mărimile) vectorilor dintr-un array de vectori.

	Parameters:
	vectors (np.ndarray): Lista de vectori.

	Returns:
	np.ndarray: Lista cu normele vectorilor.
	"""
	return np.linalg.norm(vectors, axis=1)


def cross_product_vectors(vectors1: np.ndarray, vectors2: np.ndarray) -> np.ndarray:
	"""
	Returnează produsul vectorial al vectorilor corespunzători din două arrays.

	Parameters:
	vectors1 (np.ndarray): Prima listă de vectori.
	vectors2 (np.ndarray): A doua listă de vectori.

	Returns:
	np.ndarray: Lista cu produsele vectoriale ale vectorilor corespunzători.
	"""
	return np.cross(vectors1, vectors2)


def unit_vectors(vectors: np.ndarray) -> np.ndarray:
	"""
	Returnează vectorii unitarizați pentru un array de vectori.

	Parameters:
	vectors (np.ndarray): Lista de vectori.

	Returns:
	np.ndarray: Lista cu vectorii unitarizați.
	"""
	normal_vectors = np.linalg.norm(vectors, axis=1, keepdims=True)  # Calculate norms of vectors
	normal_vectors[normal_vectors == 0] = 1  # Avoid zero division
	return vectors / normal_vectors  # Normalize vectors


# Exemplu de utilizare
if __name__ == "__main__":
	# Vectori pentru testare
	v1 = np.array([1, 0, 0])
	v2 = np.array([0, 1, 0])

	angle = calculate_angles(v1, v2)
	print(f"Unghiul dintre vectori: {angle} radiani")

	vectors_a = np.array([[1, 0, 0], [1, 1, 0], [0, 1, 0]])
	vectors_b = np.array([[0, 1, 0], [1, 0, 1], [1, 0, 0]])

	# Adunare
	added_vectors = add_vectors(vectors_a, vectors_b)
	print("Adunare:")
	print(added_vectors)

	# Scădere
	subtracted_vectors = subtract_vectors(vectors_a, vectors_b)
	print("Scădere:")
	print(subtracted_vectors)

	# Produsul Scalar
	dot_products = dot_product_vectors(vectors_a, vectors_b)
	print("Produsul Scalar:")
	print(dot_products)

	# Normele Vectoarelor
	norms = norms_of_vectors(vectors_a)
	print("Normele Vectoarelor:")
	print(norms)

	# Produsul Vectorial
	cross_products = cross_product_vectors(vectors_a, vectors_b)
	print("Produsul Vectorial:")
	print(cross_products)

	# Vectori Unitarizati
	unit_vectors_a = unit_vectors(vectors_a)
	print("Vectori Unitarizati:")
	print(unit_vectors_a)
