"""Read-only R11 diagnostic for single-phase 2D closed Fluent HDF snapshots.

Requires NumPy/h5py. No solver invocation. Exact stored mass flux accounting;
boundary-state enthalpy is explicitly an approximation, not full energy flux.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re


def mass_budget(c0, c1, flux, selected, ncell):
    """Stored flux positive from c0 toward c1/outside; c1 covers interior prefix."""
    if len(c0) != len(flux) or len(c1) > len(c0):
        raise ValueError('Inconsistent connectivity lengths')
    selected = set(selected)
    if not selected <= set(range(ncell)):
        raise ValueError('Invalid selected cell')
    divergence = [0.0] * ncell
    crossing = []
    for f, (a, q) in enumerate(zip(c0, flux)):
        b = c1[f] if f < len(c1) else None
        if not (0 <= a < ncell and (b is None or 0 <= b < ncell) and math.isfinite(q)):
            raise ValueError('Invalid face connectivity or flux')
        divergence[a] += q
        if b is not None:
            divergence[b] -= q
        sign = int(a in selected) - int(b in selected)
        if sign:
            crossing.append((f, sign * q))
    signed = math.fsum(divergence[c] for c in selected)
    boundary = math.fsum(q for _, q in crossing)
    return {'cells': len(selected), 'signed_divergence_kg_s': signed,
            'crossing_flux_kg_s': boundary, 'closure_error_kg_s': signed-boundary,
            'absolute_divergence_L1_kg_s': math.fsum(abs(divergence[c]) for c in selected)}, crossing


def shifted_energy(net_energy, net_mass, delta_h):
    """Gauge change in enthalpy: Q' = Q + delta_h * mass imbalance."""
    return net_energy + delta_h * net_mass


def read_snapshot(stem, out):
    import h5py
    import numpy as np
    case, data = Path(str(stem)+'.cas.h5'), Path(str(stem)+'.dat.h5')
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (case,data)}
    with h5py.File(case,'r') as c, h5py.File(data,'r') as d:
        m = c['meshes/1']; cf = d['results/1/phase-1/cells']; ff = d['results/1/phase-1/faces']
        xy = next(iter(m['nodes/coords'].values()))[:]
        nodes = m['faces/nodes/1/nodes'][:].astype(int).reshape(-1,2)-1
        c0 = m['faces/c0/1'][:].astype(int)-1; c1 = m['faces/c1/1'][:].astype(int)-1
        nc = int(m['cells/zoneTopology/maxId'][0]); nf = len(c0)
        names = m['faces/zoneTopology/name'][0].decode().split(';')
        zones = {z: np.arange(int(a)-1,int(b)) for z,a,b in zip(names,m['faces/zoneTopology/minId'][:],m['faces/zoneTopology/maxId'][:])}
        assert set(zones)=={'interior','inlet','outlet','top','bottom'}
        assert np.array_equal(zones['interior'],np.arange(len(c1)))
        def face_field(name):
            value = np.full((nf,)+(ff[name+'/1'].shape[1:]),np.nan)
            for ds in ff[name].values():
                a,b = int(ds.attrs['minId'][0])-1,int(ds.attrs['maxId'][0]);value[a:b]=ds[:]
            return value
        flux=face_field('SV_FLUX'); mid=xy[nodes].mean(axis=1)
        cn=[set() for _ in range(nc)]
        for i,ids in enumerate(nodes):
            cn[c0[i]].update(ids)
            if i<len(c1):cn[c1[i]].update(ids)
        centers=np.empty((nc,2));area=np.empty(nc);aspect=np.empty(nc)
        for i,ids in enumerate(cn):
            assert len(ids)==4
            v=xy[list(ids)];center=v.mean(axis=0)
            v=v[np.argsort(np.arctan2(v[:,1]-center[1],v[:,0]-center[0]))]
            nxt=np.roll(v,-1,axis=0);cross=v[:,0]*nxt[:,1]-nxt[:,0]*v[:,1]
            area[i]=cross.sum()/2;centers[i]=((v+nxt)*cross[:,None]).sum(axis=0)/(6*area[i])
            edge=np.linalg.norm(nxt-v,axis=1);aspect[i]=edge.max()/edge.min()
        assert np.all(area>0)
        edge=xy[nodes[:,1]]-xy[nodes[:,0]];normal=np.column_stack((edge[:,1],-edge[:,0]))
        distance=mid-centers[c0];normal[(normal*distance).sum(axis=1)<0]*=-1
        distance[:len(c1)]=centers[c1]-centers[c0[:len(c1)]]
        cosine=np.abs((normal*distance).sum(axis=1))/(np.linalg.norm(normal,axis=1)*np.linalg.norm(distance,axis=1))
        quality=np.ones(nc)
        np.minimum.at(quality,c0,cosine);np.minimum.at(quality,c1,cosine[:len(c1)])
        top=xy[np.unique(nodes[zones['top']])];top=top[np.argsort(top[:,0])]
        H=0.04399788;dist=np.interp(centers[:,0],top[:,0],top[:,1])-centers[:,1]
        masks={'all':np.ones(nc,dtype=bool),'downstream':centers[:,0]>=5*H,
               'upper_downstream':(centers[:,0]>=5*H)&(dist>=0)&(dist<=0.0005),
               'exit_last_H':centers[:,0]>=xy[:,0].max()-H}
        budgets={};crossrows=[]
        for name,mask in masks.items():
            b,crossing=mass_budget(c0,c1,flux,np.flatnonzero(mask),nc)
            assert abs(b['closure_error_kg_s'])<1e-10
            b.update({'min_area_m2':float(area[mask].min()),'max_edge_ratio':float(aspect[mask].max()),
                'min_normal_center_cosine':float(quality[mask].min()),'min_u_m_s':float(cf['SV_U/1'][:][mask].min()),
                'reverse_u_cells':int((cf['SV_U/1'][:][mask]<0).sum())})
            budgets[name]=b
            crossrows.extend((name,f+1,float(mid[f,0]/H),float(mid[f,1]),q) for f,q in crossing)
        fields={key:cf[key+'/1'][:] for key in ('SV_T','SV_H','SV_U','SV_V','SV_P','SV_K','SV_DENSITY')}
        ft,fu,fv,fp,fk=[face_field(key) for key in ('SV_T','SV_U','SV_V','SV_P','SV_K')]
        shear=face_field('SV_WALL_SHEAR');heat=face_field('SV_HEAT_FLUX')
        # Verify the density-solver sensible enthalpy zero from this stored field.
        cp=1004.5
        hdiff=fields['SV_H']-cp*fields['SV_T']
        h0=cp*ft+0.5*(fu**2+fv**2)
        boundary={}
        for zone in ('inlet','outlet','top','bottom'):
            z=zones[zone]
            boundary[zone]={'stored_outward_mass_kg_s':float(flux[z].sum()),
                'boundary_state_enthalpy_outward_W':float((flux[z]*cp*ft[z]).sum()),
                'boundary_state_kinetic_outward_W':float((flux[z]*0.5*(fu[z]**2+fv[z]**2)).sum()),
                'boundary_state_h0_outward_W':float((flux[z]*h0[z]).sum()),
                'mass_times_k_outward_W_NOT_ADDED':float((flux[z]*fk[z]).sum()),
                'stored_heat_flux_min_raw':float(heat[z].min()),'stored_heat_flux_max_raw':float(heat[z].max()),
                'min_u_m_s':float(fu[z].min()),'reverse_flux_faces':int((flux[z]<0).sum()),
                'p_min_Pa':float(fp[z].min()),'p_max_Pa':float(fp[z].max())}
        wallrows=[]
        for zone in ('bottom','top'):
            for f in sorted(zones[zone],key=lambda i:mid[i,0]):
                cell=c0[f];tangent=edge[f]/np.linalg.norm(edge[f]);tangent*=1 if tangent[0]>=0 else -1
                wallrows.append((zone,int(f+1),mid[f,0]/H,mid[f,1],fp[f]/(19.58*6894.757293168),
                   fields['SV_U'][cell],fields['SV_V'][cell],float(shear[f,:2]@tangent),float(np.linalg.norm(shear[f,:2])),
                   area[cell],aspect[cell],quality[cell],fields['SV_P'][cell],fields['SV_T'][cell]))
        rp=c['settings/Rampant Variables'][0].decode()
        settings=[s for s in rp.splitlines() if re.match(r'^\((?:report/energy-flux|reference-depth|operating-pressure|rp-unsteady|viscous-energy|rf-energy|rp-seg)',s)]
        result={'hashes':hashes,'cells':nc,'faces':nf,'H_m':H,'x_extent_H':[float(xy[:,0].min()/H),float(xy[:,0].max()/H)],
            'budgets':budgets,'boundary':boundary,'cell_SV_H_minus_cpT_range_J_kg':[float(hdiff.min()),float(hdiff.max())],
            'settings':settings,'stored_cell_fields':list(cf.keys()),'stored_face_fields':list(ff.keys()),
            'outlet_max_Mach_approx':float(np.max(np.hypot(fu[zones['outlet']],fv[zones['outlet']])/np.sqrt(1.4*287.05*ft[zones['outlet']]))),
            'limits':['Normal-center cosine and edge ratio are independent geometry diagnostics, not Fluent orthogonal quality/aspect ratio.',
                      'Boundary-state h0 times stored mass flux is not the exact coupled energy numerical flux.',
                      'No interior energy face flux, exact viscous/conductive face reconstruction, or physical storage term is available.',
                      'Stored wall shear sign is retained without assuming whether it is wall-on-fluid traction.']}
    assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (case,data)}
    out.mkdir(parents=True,exist_ok=False)
    (out/'audit.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    for name,header,rows in [
        ('crossing_faces.csv',['region','face_id','x_H','y_m','signed_outward_mass_kg_s'],crossrows),
        ('wall_fields.csv',['wall','face_id','x_H','y_m','p_p0','adjacent_u_m_s','adjacent_v_m_s','stored_tangent_shear_raw','stored_shear_magnitude_raw','cell_area_m2','edge_ratio','normal_center_cosine','cell_pressure_Pa','cell_T_K'],wallrows)]:
        with (out/name).open('w',newline='') as f:
            w=csv.writer(f);w.writerow(header);w.writerows(rows)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stem',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();r=read_snapshot(a.stem,a.out)
    print(json.dumps({'cells':r['cells'],'budgets':r['budgets'],'boundary':r['boundary']},indent=2))
