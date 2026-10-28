import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from compare_reference import genplot,H,NASA_X_SCALE


class ReferenceChecks(unittest.TestCase):
    def test_coordinate_scale_and_declared_count(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'synthetic.gen'
            p.write_text('synthetic\nx\np\n1\nZONE 1\n2\n0 0.8\n1 0.9\n')
            self.assertAlmostEqual(genplot(p)[1][0],1/(H*NASA_X_SCALE))
            p.write_text(p.read_text().replace('ZONE 1\n2','ZONE 1\n3'))
            with self.assertRaises(ValueError):genplot(p)

    def test_no_silent_unsorted_profile(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'synthetic.gen';p.write_text('ZONE 1\n2\n1 0.8\n0 0.9\n')
            with self.assertRaises(ValueError):genplot(p)


if __name__=='__main__':unittest.main()
