import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('audit',Path(__file__).parents[1]/'audit_r09.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class AuditTests(unittest.TestCase):
    def test_signed_flux_and_denominator(self):
        value=m.signed_budget({'inlet':10,'outlet':-9,'wall':.5})
        self.assertEqual(value['signed_sum'],1.5)
        self.assertEqual(value['relative_gap'],.15)
        self.assertEqual(m.signed_budget({'inlet':9,'outlet':-10})['relative_gap'],.1)
        with self.assertRaises(ValueError):m.signed_budget({'inlet':0,'outlet':0})

    def test_completed_log_and_truncation(self):
        report='''Mass Flow Rate [kg/s]
----- -----
inlet 10
Mass Flow Rate [kg/s]
----- -----
outlet -9.6
Total Heat Transfer Rate [W]
----- -----
bottom 0
inlet 100
outlet -98
top 0
Net 2
'''
        text=''
        for marker,start,stop in [('START_5000',5001,5101),('ITER_100',5101,5201),('ITER_200',5201,5201)]:
            text+='R09_control_cfl05_'+marker+'\n'+report
            text+=''.join(f'{i} 1e-2 2e-2 3e-2 4e-2 5e-2 6e-2 0:00:00 1\n' for i in range(start,stop))
        text+='Static Pressure [Pa]\n----- -----\ntop 90000\nStatic Pressure [Pa]\n----- -----\nbottom 80000\nR09_control_cfl05_COMPLETE\n'
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'console.log';p.write_text(text)
            v=m.parse_log(p,'control_cfl05')
            self.assertAlmostEqual(v['monitor_states']['ITER_200']['mass_kg_s']['relative_gap'],.04)
            self.assertAlmostEqual(v['monitor_states']['ITER_100']['reported_heat_W']['relative_gap'],.02)
            self.assertEqual(v['final_wall_area_mean_pressure_Pa']['bottom'],80000)
            self.assertEqual(v['residuals']['continuity']['final'],.01)
            self.assertEqual(v['status'],'SCIENTIFIC_HOLD')
            p.write_text(text.replace('R09_control_cfl05_ITER_100','missing'))
            with self.assertRaises(ValueError):m.parse_log(p,'control_cfl05')
            p.write_text(text.replace('R09_control_cfl05_COMPLETE','missing'))
            with self.assertRaises(ValueError):m.parse_log(p,'control_cfl05')


if __name__=='__main__':unittest.main()
