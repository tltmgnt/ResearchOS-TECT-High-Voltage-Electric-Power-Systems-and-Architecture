import copy,math,subprocess,sys,tempfile,unittest
from pathlib import Path
from researchos_power.model import analyze,solve
from researchos_power.records import ValidationError,dumps,read_json,sha,validate
from researchos_power.workflow import run,verify_bundle,verify_evidence
ROOT=Path(__file__).resolve().parents[1];EXAMPLE=ROOT/'examples/synthetic-power.json'

class PowerTests(unittest.TestCase):
    def setUp(self):self.r=read_json(EXAMPLE)
    def test_single_branch_analytic_high_voltage_solution(self):
        nodes=[{'id':'load','label':'Fixture','parent':'source','load_kw':1000,'line_resistance_ohm':2,'max_current_a':1000,'min_voltage_fraction':.1}]
        s=copy.deepcopy(self.r['scenarios'][0]);s['source_voltage_kv']=10
        result=solve(nodes,s);self.assertEqual(result['status'],'converged');expected=(10000+math.sqrt(10000**2-4*2*1e6))/2
        self.assertAlmostEqual(result['node_results'][0]['voltage_kv']*1000,expected,places=5)
        self.assertAlmostEqual(result['node_results'][0]['branch_current_a'],1e6/expected,places=6)
    def test_kcl_voltage_and_energy_residuals(self):
        r=analyze(self.r)['scenario_results'][0];rows={n['node_id']:n for n in r['node_results']}
        self.assertEqual(r['status'],'converged')
        self.assertAlmostEqual(rows['feeder']['branch_current_a'],2000/rows['feeder']['voltage_kv']+rows['downstream']['branch_current_a'],places=8)
        self.assertLess(abs(r['metrics']['energy_balance_residual_w']),.01)
        self.assertLess(r['metrics']['max_voltage_equation_residual_v'],.001)
        self.assertAlmostEqual(r['metrics']['source_power_mw'],r['metrics']['total_load_mw']+r['metrics']['line_losses_kw']/1000,places=8)
    def test_voltage_sensitivity_and_criteria(self):
        a,b,c=analyze(self.r)['scenario_results']
        self.assertLess(b['metrics']['line_losses_kw'],a['metrics']['line_losses_kw'])
        self.assertEqual(b['assessment'],'no-declared-limit-violations')
        self.assertIn('feeder:current',a['declared_limit_violations'])
        self.assertIn('source:power',c['declared_limit_violations'])
        self.r['scenarios'][1]['source_power_limit_mw']=None
        self.assertEqual(analyze(self.r)['scenario_results'][1]['assessment'],'source-limit-unknown')
    def test_failure_is_not_success_and_no_data(self):
        s=copy.deepcopy(self.r['scenarios'][0]);s['source_voltage_kv']=.001
        failed=solve(self.r['nodes'],s);self.assertEqual(failed['status'],'not-solved');self.assertIsNone(failed['metrics']);self.assertEqual(failed['node_results'],[]);self.assertEqual(failed['assessment'],'not-assessed-solver-failure')
        failed=solve(self.r['nodes'],self.r['scenarios'][0],max_iterations=1)
        self.assertEqual(failed['failure_reason'],'iteration-limit')
    def test_zero_load_loss_and_order_independence(self):
        expected=analyze(self.r);r=copy.deepcopy(self.r);r['nodes'].reverse();self.assertEqual(analyze(r),expected)
        for n in self.r['nodes']:n['load_kw']=0
        result=analyze(self.r)['scenario_results'][0];self.assertEqual(result['metrics']['line_losses_kw'],0);self.assertEqual(result['metrics']['source_power_mw'],0);self.assertIsNone(result['metrics']['efficiency_fraction'])
    def test_invalid_graphs_and_records(self):
        mutations=[lambda r:r.update(schema_version=True),lambda r:r.update(id='../escape'),lambda r:r['nodes'][0].update(parent='unknown'),lambda r:r['nodes'][0].update(parent='downstream'),lambda r:r['nodes'][0].update(load_kw=-1),lambda r:r['nodes'][0].update(max_current_a=True),lambda r:r['nodes'][0].update(min_voltage_fraction=2),lambda r:r['scenarios'][0].update(source_voltage_kv=0),lambda r:r.update(data_kind='experimental')]
        for mutate in mutations:
            r=copy.deepcopy(self.r);mutate(r)
            with self.subTest(record=r),self.assertRaises(ValidationError):validate(r)
    def test_experimental_evidence_and_portability(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=b'fixture, not real HV evidence';(root/'raw').write_bytes(data);self.r['data_kind']='experimental';self.r['evidence']=[{'id':'raw','path':'raw','sha256':sha(data),'description':'Test only'}];self.r['measurements']=[{'metric':'source power','unit':'MW','value':5,'uncertainty':.1,'method':'Fixture','evidence_ids':['raw']}]
            p=root/'record.json';p.write_text(dumps(self.r));run(p,root/'run');(root/'raw').unlink();verify_bundle(root/'run');(root/'run/evidence/0000.bin').write_bytes(b'changed')
            with self.assertRaises(ValidationError):verify_bundle(root/'run')
    def test_integrity_paths_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);a,b=root/'a',root/'b';run(EXAMPLE,a);run(EXAMPLE,b);verify_bundle(a);self.assertEqual({p.relative_to(a):p.read_bytes() for p in a.rglob('*') if p.is_file()},{p.relative_to(b):p.read_bytes() for p in b.rglob('*') if p.is_file()})
            with self.assertRaises(ValidationError):run(EXAMPLE,a)
            result=read_json(a/'results.json');result['scenario_results'][0]['metrics']['line_losses_kw']=0;(a/'results.json').write_text(dumps(result));manifest=read_json(a/'manifest.json');manifest['files']['results.json']=sha((a/'results.json').read_bytes());(a/'manifest.json').write_text(dumps(manifest))
            with self.assertRaises(ValidationError):verify_bundle(a)
            self.r['evidence']=[{'id':'raw','path':'../escape','sha256':sha(b'x'),'description':'Fixture'}]
            with self.assertRaises(ValidationError):validate(self.r)
            (root/'link').symlink_to(root.parent);self.r['evidence'][0]['path']='link/outside'
            with self.assertRaises(ValidationError):verify_evidence(validate(self.r),root)
    def test_strict_json_and_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'bad.json'
            for data in ['{"x":1,"x":2}','{"x":NaN}']:
                p.write_text(data)
                with self.assertRaises(ValidationError):read_json(p)
            output=str(Path(tmp)/'run')
            for args in [['validate',str(EXAMPLE)],['run',str(EXAMPLE),'--output',output],['verify',output],['report',output]]:
                r=subprocess.run([sys.executable,'-m','researchos_power',*args],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)
