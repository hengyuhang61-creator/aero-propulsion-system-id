"""R11: compare NASA numerical GENPLOT, experimental text and closed Fluent walls.

Uses each case's p/p0 and a common H=0.04399788 m. Different thermal conditions
are retained as a comparability limitation, not silently transformed away.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from compare_steady import parse,interp,shock,err

H=0.04399788
NASA_X_SCALE=22.7273  # m^-1, explicitly in cfpost.p.{top,bot}.com


def genplot(path):
    lines=path.read_text().splitlines()
    zones=[i for i,line in enumerate(lines) if line.strip().startswith('ZONE')]
    if len(zones)!=1:raise ValueError('Expected one GENPLOT zone')
    i=zones[0];n=int(lines[i+1]);rows=[]
    for line in lines[i+2:]:
        if not line.strip():continue
        x,p=map(float,line.split())
        x=x/(NASA_X_SCALE*H)
        if not (math.isfinite(x) and math.isfinite(p) and 0<p<1.1):raise ValueError('Invalid GENPLOT value')
        if rows and x<=rows[-1][0]:raise ValueError('Unsorted GENPLOT stations')
        rows.append((x,p))
    if len(rows)!=n or n<2:raise ValueError('GENPLOT count mismatch')
    return rows


def compare(nasa_dir,experiment,local_paths,out):
    inputs=[experiment,nasa_dir/'p.top.5sst.gen',nasa_dir/'p.bot.5sst.gen']+local_paths
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    experimental=parse(experiment)
    curves={'NASA_WIND5_SST':{w:genplot(nasa_dir/f'p.{z}.5sst.gen') for w,z in [('top','top'),('bottom','bot')]}}
    for path in local_paths:
        if path.parent.name in curves:raise ValueError('Duplicate case label')
        rows=list(csv.DictReader(path.open()))
        curves[path.parent.name]={w:sorted((float(r['x_H']),float(r['p_p0'])) for r in rows if r['wall']==w) for w in experimental}
        for wall,values in curves[path.parent.name].items():
            if len(values)<2 or any(not (math.isfinite(x) and math.isfinite(p)) for x,p in values):raise ValueError('Invalid local wall data')
            if any(a[0]>=b[0] for a,b in zip(values,values[1:])):raise ValueError('Duplicate local station')
    metrics={};records=[]
    for wall,obs in experimental.items():
        lower=max(c[wall][0][0] for c in curves.values());upper=min(c[wall][-1][0] for c in curves.values())
        points=[(x,p) for x,p in obs if lower<=x<=upper]
        reference=[interp(curves['NASA_WIND5_SST'][wall],x) for x,_ in points]
        measured=[p for _,p in points]
        metrics[wall]={'common_x_H':[lower,upper],'n':len(points),'experimental_shock':shock(obs),'cases':{}}
        for name,c in curves.items():
            prediction=[interp(c[wall],x) for x,_ in points]
            metrics[wall]['cases'][name]={'vs_experiment':err(measured,prediction),'vs_NASA_numerical':err(reference,prediction),'shock':shock(c[wall]),
                'shock_delta_vs_experiment_H':shock(c[wall])['midpoint_x_over_H']-shock(obs)['midpoint_x_over_H']}
            for (x,p),n,v in zip(points,reference,prediction):records.append((wall,name,x,p,n,v,v-p,v-n))
    result={'source_sha256':{p.name+'@'+p.parent.name:hashes[str(p)] for p in inputs},'H_m':H,'NASA_p0_psia_inferred_gamma1p4':16.937*(1+.2*.46**2)**3.5,
        'NASA_T0_R_inferred_gamma1p4':504.26*(1+.2*.46**2),'NASA_exit_psia':16.055,
        'local_p0_psia':19.58,'local_T0_R':500.,'local_exit_psia':16.05,
        'experimental_header_T0_K':300.,'metrics':metrics,
        'limitations':['Numerical reference is not experimental measurement.',
            'Local fields fail numerical qualification; agreement cannot validate them.',
            'Study 3 static input implies T0=525.6002832 R, distinct from local 500 R and experimental 540 R.',
            'Common dimensionless pressure profiles are a conditional diagnostic, not exact matched-Reynolds validation.',
            'Fluent wall-face centers and WIND exported stations differ; interpolation uses experimental stations in common coverage only.',
            'Shock sampling intervals are not statistical confidence intervals.']}
    assert hashes=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    out.mkdir(parents=True,exist_ok=False)
    (out/'reference_summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    with (out/'reference_comparison.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['wall','case','x_H','experiment_p_p0','NASA_numerical_p_p0','case_p_p0','case_minus_experiment','case_minus_NASA']);w.writerows(records)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--nasa-dir',type=Path,required=True)
    p.add_argument('--experiment',type=Path,required=True);p.add_argument('--local',type=Path,action='append',required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();r=compare(a.nasa_dir,a.experiment,a.local,a.out);print(json.dumps(r['metrics'],indent=2))
