"""Two-condition NASA Sajben wall-pressure contrast, with no model fitting."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

ZONES = {'inlet_near_throat':(-1.1,0.0), 'shock_region':(0.5,3.2),
         'downstream':(3.2,8.0), 'all_overlap':(-4.0,8.0)}
FROZEN_HASHES = {'weak':'ae2541b66d71e7ede514d3572965b00d1ca2510747ba4b8b2fd92690f4f1b167',
                 'strong':'5d58b25b6d4da51ff3a79a8b38529474df5490b5b5cb54c3abef0f6947f7f217'}
DELTA_BACK_PRESSURE = 0.72 - 0.82


def parse(path):
    """Preserve order; collapse adjacent duplicate stations only if p agrees."""
    walls = {'bottom':[], 'top':[]}
    for number, line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
        line = line.strip()
        if not line or line.startswith('#') or line.upper().startswith(('VARIABLES','ZONE')):
            continue
        fields = line.split()
        if len(fields) != 4:
            raise ValueError(f'Line {number}: expected four columns')
        vals = [float(v) for v in fields]
        for wall, (x,p) in zip(walls, ((vals[0],vals[1]),(vals[2],vals[3]))):
            if not (math.isfinite(x) and math.isfinite(p) and 0 < p < 1.1):
                raise ValueError(f'Line {number}: nonfinite or out-of-range x,p/p0')
            if walls[wall] and x == walls[wall][-1][0]:
                if abs(p-walls[wall][-1][1]) > 1e-12:
                    raise ValueError(f'Line {number}: conflicting duplicate x')
                continue
            if walls[wall] and x <= walls[wall][-1][0]:
                raise ValueError(f'Line {number}: stations must increase')
            walls[wall].append((x,p))
    if any(len(v)<2 for v in walls.values()):
        raise ValueError('At least two distinct stations per wall required')
    return walls


def interp(obs, x):
    """Piecewise linear spatial interpolation; no extrapolation."""
    if x < obs[0][0] or x > obs[-1][0]:
        return None
    for (a,pa),(b,pb) in zip(obs,obs[1:]):
        if a <= x <= b:
            return pa + (pb-pa)*(x-a)/(b-a)
    return obs[-1][1]


def shock(obs):
    """Max positive adjacent slope with midpoint in [0,4]H; rightmost tie."""
    slopes = [((pb-pa)/(b-a),a,b) for (a,pa),(b,pb) in zip(obs,obs[1:]) if 0 <= (a+b)/2 <= 4]
    if not slopes or max(slopes)[0] <= 0:
        raise ValueError('No positive pressure rise in the shock search interval')
    slope,a,b = max(slopes)
    return {'midpoint_x_over_H':(a+b)/2, 'interval_x_over_H':[a,b],
            'max_positive_gradient_per_H':slope}


def err(target, prediction):
    if not target or len(target)!=len(prediction):
        raise ValueError('Empty or unequal comparison vectors')
    residual = [a-b for a,b in zip(target,prediction)]
    return {'rmse':math.sqrt(sum(r*r for r in residual)/len(residual)),
            'mae':sum(abs(r) for r in residual)/len(residual), 'n':len(residual)}


def compare(raw):
    walls,rows = {},[]
    for wall in ('bottom','top'):
        weak,strong = raw['weak'][wall],raw['strong'][wall]
        sw,ss = shock(weak),shock(strong)
        scores = {}
        for zone,(lower,upper) in ZONES.items():
            picked = [(x,p,interp(strong,x)) for x,p in weak if lower <= x <= upper]
            picked = [(x,p,q) for x,p,q in picked if q is not None]
            if not picked:
                raise ValueError(f'No overlapping stations: {wall}/{zone}')
            target = [q for _,_,q in picked]
            frozen = [p for _,p,_ in picked]
            uniform = [p+DELTA_BACK_PRESSURE for p in frozen]
            scores[zone] = {'freeze_output':err(target,frozen), 'uniform_unit_gain':err(target,uniform),
                            'mean_signed_delta':statistics.mean(q-p for _,p,q in picked),
                            'mean_abs_delta':statistics.mean(abs(q-p) for _,p,q in picked)}
            for x,p,q in picked:
                rows.append({'wall':wall,'zone':zone,'x_over_H':x,'weak_p_over_p0':p,
                             'strong_interpolated_p_over_p0':q,'measured_delta':q-p,
                             'frozen_prediction':p,'uniform_gain_prediction':p+DELTA_BACK_PRESSURE})
        walls[wall] = {'original_sample_counts':{'weak':len(weak),'strong':len(strong)},
                        'shock_weak':sw,'shock_strong':ss,
                        'shock_shift_x_over_H':ss['midpoint_x_over_H']-sw['midpoint_x_over_H'],
                        'shift_interval_from_sampling':[ss['interval_x_over_H'][0]-sw['interval_x_over_H'][1],
                                                        ss['interval_x_over_H'][1]-sw['interval_x_over_H'][0]],
                        'zone_metrics':scores}
    return walls,rows


def verify_frozen(hashes,walls):
    if hashes!=FROZEN_HASHES:
        raise ValueError('Input SHA-256 differs from frozen NASA files; investigate provenance')
    for wall,expected in [('bottom',0.8585),('top',0.7665)]:
        if not math.isclose(walls[wall]['shock_shift_x_over_H'],expected,rel_tol=0,abs_tol=1e-12):
            raise ValueError('Frozen shock-shift regression failed')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--weak',type=Path,required=True)
    parser.add_argument('--strong',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True,help='New output directory; refuses overwrite')
    parser.add_argument('--verify-frozen',action='store_true',help='Require exact NASA hashes and known shifts')
    args=parser.parse_args()
    files={'weak':args.weak,'strong':args.strong}
    hashes={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in files.items()}
    walls,rows=compare({k:parse(p) for k,p in files.items()})
    if args.verify_frozen:verify_frozen(hashes,walls)
    if hashes!={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in files.items()}:
        raise RuntimeError('Inputs changed during calculation')
    result={'source_files':{k:{'name':p.name,'sha256':hashes[k]} for k,p in files.items()},
            'source_url':'https://www.grc.nasa.gov/WWW/wind/valid/transdif/transdif02/transdif02.html',
            'physical_input':{'weak_p_exit_over_p0':.82,'strong_p_exit_over_p0':.72,'delta_exit_ratio':DELTA_BACK_PRESSURE},
            'units':{'x':'x / throat height H','pressure':'wall static p / inlet total p0'},
            'walls':walls,
            'status':{'steady_contrast':'COMPUTED','dynamic_identification':'HOLD_NO_TIME_SERIES_OR_EXCITATION',
                      'surrogate_validation':'HOLD_ONLY_TWO_STEADY_CASES','novelty':'UNKNOWN_NOT_CLAIMED'},
            'limitations':['Two conditions are not statistical replicates.','Sampling intervals are not confidence intervals.',
                           'Overlapping spatial zones are not independent samples.','No CFD convergence or dynamic transfer is inferred.']}
    args.out.mkdir(parents=True,exist_ok=False)
    (args.out/'experiment_result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    with (args.out/'contrast_points.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps({w:walls[w]['shock_shift_x_over_H'] for w in walls}))


if __name__=='__main__':
    main()
