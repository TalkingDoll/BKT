"""Publish per-realisation data for the retained manuscript configurations."""
from __future__ import annotations
import copy
from revision_common import ROOT,write_json,PRODUCT_SEED_INDICES

def selected_summary(summary):
    result=copy.deepcopy(summary)
    assert len(result['alanine_rows'])==20
    assert {r['fit_trajectory'] for r in result['alanine_rotations']}=={0}
    result['presentation_scope']='Fixed configurations, with all prescribed realisations retained. Alanine uses trajectory 1 for fitting and source construction; no across-fit robustness claim is made.'
    return result

def export_public(data,summary):
    def clean(value):
        if isinstance(value,dict):return {k:clean(v) for k,v in value.items() if k!='filepath'}
        if isinstance(value,list):return [clean(v) for v in value]
        return value
    record=dict(format=1,scope='Retained manuscript configurations and per-realisation records; arrays remain in local archives.',
        trajectory_indexing='JSON uses zero-based indices; the report uses trajectories 1, 2, 3.',
        rows=data,summary=selected_summary(summary),counts={k:len(v) for k,v in data.items()},
        active_product_indices=list(PRODUCT_SEED_INDICES))
    write_json(ROOT/'outputs/revision_results.json',clean(record))
