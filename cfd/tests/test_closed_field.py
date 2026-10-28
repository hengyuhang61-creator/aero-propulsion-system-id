import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from closed_field_audit import mass_budget, shifted_energy


class ClosedFieldChecks(unittest.TestCase):
    def test_internal_cancellation_and_subregion(self):
        # Two cells: internal 3, left inflow -2, right outflow 2.5.
        c0,c1,q=[0,0,1],[1],[3.,-2.,2.5]
        all_cells,_=mass_budget(c0,c1,q,[0,1],2)
        left,_=mass_budget(c0,c1,q,[0],2)
        self.assertEqual(all_cells['signed_divergence_kg_s'],.5)
        self.assertEqual(all_cells['absolute_divergence_L1_kg_s'],1.5)
        self.assertEqual(left['crossing_flux_kg_s'],1.)
        self.assertEqual(left['closure_error_kg_s'],0.)

    def test_invalid_connectivity(self):
        with self.assertRaises(ValueError):mass_budget([2],[],[1.],[0],2)
        with self.assertRaises(ValueError):mass_budget([0],[],[float('nan')],[0],1)

    def test_enthalpy_datum_depends_on_mass_defect(self):
        self.assertEqual(shifted_energy(10.,0.,300000.),10.)
        self.assertEqual(shifted_energy(10.,.2,-300000.),-59990.)


if __name__=='__main__':unittest.main()
