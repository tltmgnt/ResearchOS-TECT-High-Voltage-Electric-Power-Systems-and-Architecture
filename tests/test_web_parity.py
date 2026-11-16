import copy,json,math,shutil,subprocess,unittest
from pathlib import Path
from researchos_power.model import analyze
from researchos_power.records import read_json
ROOT=Path(__file__).resolve().parents[1]
@unittest.skipUnless(shutil.which('node'),'Node required for web parity')
class WebParityTests(unittest.TestCase):
    def test_full_model_parity(self):
        base=read_json(ROOT/'examples/synthetic-power.json');cases=[base]
        r=copy.deepcopy(base);r['nodes'].reverse();r['scenarios'][0]['source_power_limit_mw']=None;cases.append(r)
        r=copy.deepcopy(base)
        for n in r['nodes']:n['load_kw']=0
        cases.append(r)
        r=copy.deepcopy(base);r['scenarios'][0]['source_voltage_kv']=.001;cases.append(r)
        js="import fs from 'node:fs';import{analyze}from './web/model.mjs';console.log(JSON.stringify(JSON.parse(fs.readFileSync(0,'utf8')).map(analyze)))"
        results=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],input=json.dumps(cases),text=True,cwd=ROOT))
        def compare(a,b):
            if isinstance(b,dict):
                self.assertEqual(a.keys(),b.keys())
                for k in b:compare(a[k],b[k])
            elif isinstance(b,list):
                self.assertEqual(len(a),len(b))
                for x,y in zip(a,b):compare(x,y)
            elif type(b) is float:self.assertTrue(math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-6),(a,b))
            else:self.assertEqual(a,b)
        for r,w in zip(cases,results):compare(w,analyze(r))
