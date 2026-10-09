"""New exporter/audit component tests; NOT the author's six Stage0B tests."""
import tempfile, unittest
from pathlib import Path
import h5py
import numpy as np
import pandas as pd
from scipy import sparse
from export_wp1_prefit import vector,align_index,overlap_map,selected_counts_and_totals,axis_scores,t0_log,aggregate,matrix_rank_elimination
from audit_stage0b import resolve_stage_path

class PrefitTests(unittest.TestCase):
    def test_01_identity_alignment(self):
        np.testing.assert_array_equal(align_index([8,1,4],[4,8,1]),[1,2,0])
    def test_02_alignment_rejects_duplicate(self):
        with self.assertRaises(ValueError):align_index([1,1],[1,2])
    def test_03_alignment_rejects_missing(self):
        with self.assertRaises(ValueError):align_index([1,2],[1,3])
    def test_04_overlap_majority(self):
        a,b,m,c=overlap_map(['0','1','3','3'],['x','x','y','y'])
        np.testing.assert_array_equal(a,b);self.assertEqual(m.cluster_purity_vs_A0.min(),1)
    def test_05_overlap_tie_stops(self):
        with self.assertRaises(ValueError):overlap_map(['0','3','3'],['x','x','y'])
    def test_06_unexpected_A0_stops(self):
        with self.assertRaises(ValueError):overlap_map(['0','5'],['x','y'])
    def test_07_lost_compartment_stops(self):
        with self.assertRaises(ValueError):overlap_map(['0','0','3'],['x','x','x'])
    def test_08_permutation_does_not_change_mapping(self):
        a0=np.array(['0','1','2','3','3']);a2=np.array(['x','x','x','y','y']);order=[4,0,3,1,2]
        m1=overlap_map(a0,a2)[2].sort_values('A2_cluster').reset_index(drop=True)
        m2=overlap_map(a0[order],a2[order])[2].sort_values('A2_cluster').reset_index(drop=True)
        pd.testing.assert_frame_equal(m1,m2)
    def test_09_sum_aggregation(self):
        c,t,n=aggregate(np.array([[1,2],[3,4],[5,6]]),np.array([10,20,30]),np.array([0,-1,0]),2)
        np.testing.assert_array_equal(c,[[6,8],[0,0]]);np.testing.assert_array_equal(t,[40,0]);np.testing.assert_array_equal(n,[2,0])
    def make_h5(self,path,values):
        x=sparse.csr_matrix(values)
        with h5py.File(path,'w') as h:
            v=h.create_group('var');v.create_dataset('feature_name',data=np.array(['G','OTHER','G'],dtype=object),dtype=h5py.string_dtype())
            y=h.create_group('X');y.attrs['encoding-type']='csr_matrix';y.attrs['shape']=x.shape
            for k in ['data','indices','indptr']:y.create_dataset(k,data=getattr(x,k))
    def test_10_duplicate_symbols_and_full_total(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'x.h5';self.make_h5(p,[[1,97,2],[5,20,3]])
            with h5py.File(p) as h:c,tot=selected_counts_and_totals(h,['G'],block_size=1)
            np.testing.assert_array_equal(c[:,0],[3,8]);np.testing.assert_array_equal(tot,[100,28])
    def test_11_noninteger_raw_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'x.h5';self.make_h5(p,[[1.2,2.,3.]])
            with h5py.File(p) as h:
                with self.assertRaises(ValueError):selected_counts_and_totals(h,['G'])
    def test_12_missing_gene_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'x.h5';self.make_h5(p,[[1,2,3]])
            with h5py.File(p) as h:
                with self.assertRaises(ValueError):selected_counts_and_totals(h,['ABSENT'])
    def test_13_zero_total_rejected(self):
        with self.assertRaises(ValueError):t0_log(np.ones((1,2)),[0])
    def test_14_log_blending_noncommutes(self):
        c=np.array([[1.],[9.]])
        score_first=float(t0_log(c,[1e6,1e6]).mean());expression_first=float(t0_log(np.array([[5.]]),[1e6])[0,0])
        self.assertGreater(expression_first,score_first+.5)
    def test_15_axis_uses_fixed_parameters(self):
        p=pd.DataFrame({'mean_log1p_cp10k':[0.,0.],'population_sd_log1p_cp10k':[1.,1.],'sign':[1,-1]})
        s,x=axis_scores(np.array([[2,1]]),np.array([100]),p)
        self.assertAlmostEqual(s[0],np.log1p(200)-np.log1p(100))
    def test_16_joint_support_not_marginal_minimum(self):
        x=np.array([[30,0],[0,30],[30,30]])
        self.assertEqual((x>=30).sum(axis=0).min(),2);self.assertEqual((x>=30).all(axis=1).sum(),1)
    def test_17_categorical_values(self):
        with tempfile.TemporaryDirectory() as t:
            with h5py.File(Path(t)/'c.h5','w') as h:
                g=h.create_group('g');g.create_dataset('codes',data=[1,0]);g.create_dataset('categories',data=np.array(['a','b'],dtype=object),dtype=h5py.string_dtype())
                np.testing.assert_array_equal(vector(g),['b','a'])
    def test_18_categorical_missing_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            with h5py.File(Path(t)/'c.h5','w') as h:
                g=h.create_group('g');g.create_dataset('codes',data=[-1]);g.create_dataset('categories',data=[2])
                with self.assertRaises(ValueError):vector(g)
    def test_19_stage_alias_relocation(self):
        s=Path('/tmp/20261009_stage0b')
        self.assertEqual(resolve_stage_path(s,'phase17_v7\\rp_v3_redesign\\20261009_stage0b\\a.h5ad'),(s/'a.h5ad').resolve())
    def test_20_external_input_not_invented(self):
        self.assertIsNone(resolve_stage_path(Path('/tmp/20261009_stage0b'),'phase17_v7/gateC2B1/raw.h5ad'))
    def test_21_path_traversal_stops(self):
        with self.assertRaises(ValueError):resolve_stage_path(Path('/tmp/20261009_stage0b'),'../raw.h5ad')
    def test_22_rank_without_lapack(self):
        self.assertEqual(matrix_rank_elimination([[1,0,1],[0,1,1],[1,1,2]]),2)
        self.assertEqual(matrix_rank_elimination([[1,0],[0,1],[1,1]]),2)
    def test_23_complementary_dummies_are_rank_deficient_with_intercept(self):
        design=[[1,0,1],[1,1,0],[1,0,1],[1,1,0]]
        self.assertEqual(matrix_rank_elimination(design),2)

if __name__=='__main__':unittest.main(verbosity=2)
