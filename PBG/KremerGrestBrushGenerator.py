"""
Exports the KremerGrestBrushGenerator class
"""

from enum import Enum
from typing import Optional

import numpy as np

from PBG.BrushGenerator import BrushGenerator


class KremerGrestBrushGenerator(BrushGenerator):
	"""
	Generate a LAMMPS data file containing a Kremer-Grest polymer brush grafted to a planar wall in a rectangular box.

	Kremer, K.; Grest, G. S. Dynamics of Entangled Linear Polymer Melts: A Molecular‐dynamics Simulation. J. Chem. Phys.
	1990, 92 (8), 5057–5086. https://doi.org/10.1063/1.458541.
	"""

	AtomTypes = Enum('AtomTypes', ['graft', 'bead', 'solvent'])
	BondTypes = Enum('BondTypes', ['fene'])

	masses = {
		AtomTypes.graft  : 1,
		AtomTypes.bead   : 1,
		AtomTypes.solvent: 1
	}

	styles = {
		'pair': 'lj/cut',
		'bond': 'fene',
	}

	def __init__(self, box_size: tuple[float, float, Optional[float]], rng_seed: Optional[int], n_beads: int,
	             graft: bool = True):
		"""
		:param box_size: 3-tuple of floats describing the dimensions of the rectangular box. If the third (z) value
		                 is None, it will be automatically sized to contain the longest chain.
		:param rng_seed: Seed used to initialize the PRNG. May be None, in which case a random seed will be used.
		:param n_beads:  Chain length.
		:param graft:    Generates grafted brushes when True, and non-grafted films when False
		"""
		bead_size = 1  # (sigma)
		bottom_padding = 1  # (sigma)
		self.graft = graft
		super().__init__(box_size, rng_seed, bead_size, n_beads, bottom_padding)

	def _build_bead(self, mol_id: int, graft_coord: np.ndarray, bead_id: int) -> float:
		if bead_id == 0:
			# Omit grafting bead if graft=False
			if not self.graft:
				return 0
			atom_type = self.AtomTypes.graft.value
		else:
			atom_type = self.AtomTypes.bead.value

		self._atoms_list.append({'mol_id'   : bead_id + 1,
		                         'atom_type': atom_type,
		                         'q'        : 0,
		                         'x'        : graft_coord[0],
		                         'y'        : graft_coord[1],
		                         'z'        : float(bead_id*self.bead_size)
		                         })

		# Molecular topology
		if bead_id >= 1 and self.graft or bead_id >= 2:
			atom_id = len(self._atoms_list)
			self._bonds_list.append({'bond_type': self.BondTypes.fene.value,
			                         'atom1'    : atom_id - 1,
			                         'atom2'    : atom_id
			                         })

		return float(bead_id*self.bead_size)
