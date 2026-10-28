import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('compare',Path(__file__).parents[1]/'compare_steady.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class CompareTests(unittest.TestCase):
    def parse_text(self,text):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'synthetic.data';p.write_text(text,encoding='utf-8')
            return m.parse(p)

    def test_duplicate_is_independent_per_wall(self):
        v=self.parse_text('# comment\nVARIABLES = x p x p\nZONE T=test\n0 .2 0 .3\n1 .4 1 .5\n1 .4 2 .6\n')
        self.assertEqual(v,{'bottom':[(0.,.2),(1.,.4)],'top':[(0.,.3),(1.,.5),(2.,.6)]})

    def test_reject_conflict_unsorted_nonfinite_bad_shape(self):
        for text in ['0 .2 0 .2\n0 .3 1 .4','1 .2 1 .2\n0 .3 2 .4','0 nan 0 .2\n1 .3 1 .4','0 .2 0','0 .2 0 .2']:
            with self.subTest(text=text),self.assertRaises(ValueError):self.parse_text(text)

    def test_linear_interpolation_and_closed_endpoints(self):
        obs=[(0,.2),(2,.6)]
        self.assertAlmostEqual(m.interp(obs,1),.4)
        self.assertEqual(m.interp(obs,0),.2);self.assertEqual(m.interp(obs,2),.6)
        self.assertIsNone(m.interp(obs,-1e-12));self.assertIsNone(m.interp(obs,2.00001))

    def test_shock_localization_and_search_boundary(self):
        obs=[(-2,.1),(-1,.9),(0,.1),(1,.2),(2,.8),(3,.81),(5,.82)]
        self.assertEqual(m.shock(obs)['interval_x_over_H'],[1,2])
        with self.assertRaises(ValueError):m.shock([(0,.8),(1,.7)])
        # Identical gradients deliberately choose the rightmost interval.
        self.assertEqual(m.shock([(0,.125),(1,.25),(2,.375)])['interval_x_over_H'],[1,2])

    def test_error_metrics_are_not_interchanged(self):
        result=m.err([0,0],[3,4])
        self.assertEqual(result['mae'],3.5);self.assertAlmostEqual(result['rmse'],(12.5)**.5)
        with self.assertRaises(ValueError):m.err([1],[1,2])

    def test_end_to_end_synthetic_constant_drop(self):
        weak=[(-1,.4),(0,.4),(.5,.45),(1,.5),(2,.9),(3.2,.9),(8,.9)]
        strong=[(x,p-.1) for x,p in weak]
        walls,rows=m.compare({'weak':{'bottom':weak,'top':weak},'strong':{'bottom':strong,'top':strong}})
        for wall in walls.values():
            self.assertAlmostEqual(wall['shock_shift_x_over_H'],0)
            for score in wall['zone_metrics'].values():
                self.assertAlmostEqual(score['freeze_output']['rmse'],.1)
                self.assertAlmostEqual(score['uniform_unit_gain']['rmse'],0)
        self.assertEqual(len(rows),2*(2+4+2+7))

    def test_no_overlap_and_wrong_hash_fail_closed(self):
        obs=[(-1,.4),(0,.4),(.5,.5),(1,.8),(3.2,.9),(8,.9)]
        with self.assertRaises(ValueError):m.compare({'weak':{'bottom':obs,'top':obs},'strong':{'bottom':[(x+30,p) for x,p in obs],'top':obs}})
        with self.assertRaises(ValueError):m.verify_frozen({}, {})


if __name__=='__main__':unittest.main()
