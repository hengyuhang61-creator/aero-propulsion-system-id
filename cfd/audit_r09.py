"""Recompute R09 diagnostics from completed native console logs. Stdlib only."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import statistics

NUMBER = r'[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?'
FIELDS = ('continuity', 'x_velocity', 'y_velocity', 'energy', 'k', 'omega')


def signed_budget(values):
    denominator = max(abs(values['inlet']), abs(values['outlet']))
    if denominator == 0:
        raise ValueError('Zero throughflow denominator')
    net = sum(values.values())
    return {'signed': values, 'signed_sum': net, 'denominator': denominator,
            'relative_gap': abs(net) / denominator}


def parse_log(path, branch):
    raw = path.read_bytes()
    text = raw.decode('utf-8', errors='replace')
    if not re.search(r'^R09_' + branch + r'_COMPLETE\s*$', text, re.M):
        raise ValueError('Missing standalone completion marker')
    states = {}
    chunks = re.split(r'^R09_' + branch + r'_(START_5000|ITER_100|ITER_200)\s*$', text, flags=re.M)
    if chunks[1::2] != ['START_5000', 'ITER_100', 'ITER_200']:
        raise ValueError('Missing or duplicated monitor states')
    for marker, chunk in zip(chunks[1::2], chunks[2::2]):
        mass = {}
        for zone in ('inlet', 'outlet'):
            match = re.search(r'Mass Flow Rate\s+\[kg/s\]\s*-+\s*-+\s*' + zone + r'\s+(' + NUMBER + r')', chunk)
            if match is None:
                raise ValueError('Missing mass report: ' + marker + ' ' + zone)
            mass[zone] = float(match[1])
        heat_block = re.search(r'Total Heat Transfer Rate\s+\[W\](.*?\bNet\s+(' + NUMBER + r'))', chunk, re.S)
        if heat_block is None:
            raise ValueError('Missing heat report')
        heat = {z: float(re.search(r'^\s*' + z + r'\s+(' + NUMBER + r')\s*$', heat_block[1], re.M)[1])
                for z in ('bottom', 'inlet', 'outlet', 'top')}
        states[marker] = {'mass_kg_s': signed_budget(mass), 'reported_heat_W': signed_budget(heat)}
        states[marker]['reported_heat_W']['native_net'] = float(heat_block[2])
        states[marker]['reported_heat_W']['native_net_roundoff_delta_W'] = float(heat_block[2]) - sum(heat.values())
    rows = {}
    for match in re.finditer(r'^\s*(\d+)\s+' + r'\s+'.join(['(' + NUMBER + ')'] * 6) + r'\s+\d+:\d+:\d+\s+\d+\s*$', text, re.M):
        iteration = int(match[1])
        values = tuple(float(match[i]) for i in range(2, 8))
        if iteration in rows and rows[iteration] != values:
            raise ValueError('Conflicting duplicate residual')
        rows[iteration] = values
    if sorted(i for i in rows if i > 5000) != list(range(5001, 5201)):
        raise ValueError('Not exactly 200 new residual records')
    residuals = {}
    for j, name in enumerate(FIELDS):
        windows = [[rows[i][j] for i in range(a, b)] for a, b in ((5001, 5101), (5101, 5201))]
        residuals[name] = {'final':rows[5200][j], 'first_100_median':statistics.median(windows[0]),
                           'last_100_median':statistics.median(windows[1]),
                           'minimum':min(windows[0]+windows[1]), 'maximum':max(windows[0]+windows[1])}
    wall = {}
    for zone in ('top', 'bottom'):
        match = re.search(r'Static Pressure\s+\[Pa\]\s*-+\s*-+\s*' + zone + r'\s+(' + NUMBER + r')', text)
        if match is None:
            raise ValueError('Missing wall report')
        wall[zone] = float(match[1])
    return {'log_sha256':hashlib.sha256(raw).hexdigest(), 'monitor_states':states,
            'new_iterations':200, 'residuals':residuals, 'final_wall_area_mean_pressure_Pa':wall,
            'status':'SCIENTIFIC_HOLD', 'full_energy_budget':'NOT_ESTABLISHED_BY_REPORT_LABEL',
            'two_500_iteration_windows':'NOT_AVAILABLE',
            'wall_pressure_stability':'NOT_AVAILABLE_ONE_END_REPORT_ONLY',
            'units_note':'Native 2D reports kg/s and W; modeled depth convention requires separate qualification.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True, help='Completed R09 directory')
    parser.add_argument('--out', type=Path, required=True, help='New JSON output (will not overwrite)')
    args = parser.parse_args()
    result = {b:parse_log(args.root/b/'console.log', b) for b in ('control_cfl05','test_cfl01')}
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, allow_nan=False)
    print(json.dumps({b:{'mass_gap':v['monitor_states']['ITER_200']['mass_kg_s']['relative_gap'],
                           'reported_energy_gap':v['monitor_states']['ITER_200']['reported_heat_W']['relative_gap']}
                      for b,v in result.items()}, indent=2))


if __name__ == '__main__':
    main()
