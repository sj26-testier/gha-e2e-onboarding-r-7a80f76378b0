import hashlib,json,os,pathlib,subprocess
event=json.loads(pathlib.Path(os.environ['GITHUB_EVENT_PATH']).read_text())
d=event['deployment']; s=event.get('deployment_status')
context={k:os.environ.get('CTX_'+k.upper(),'') for k in ['sha','ref','ref_name','ref_type','event_name','workflow','workflow_ref','workflow_sha']}
sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
ref=d['ref']; fullsha=len(ref)==40 and all(c in '0123456789abcdef' for c in ref)
expected_ref='' if fullsha else ('refs/tags/' if ref.startswith('deploy-tag-') else 'refs/heads/')+ref
result={'context':context,'checkout_sha':sha,'fixture':pathlib.Path('deployment-marker.txt').read_text().strip(),'workflow_marker':os.environ['WORKFLOW_MARKER'],'deployment':{k:d.get(k) for k in ['id','sha','ref','environment','original_environment','task','payload']},'status':None if s is None else {k:s.get(k) for k in ['id','state','environment','environment_url','log_url','target_url']},'event_sha256':hashlib.sha256(json.dumps(event,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),'github_env':{k:os.environ.get('GITHUB_'+k.upper(),'') for k in ['sha','ref','ref_name','ref_type','event_name']}}
assert sha==d['sha']==context['sha'],result
assert context['ref']==expected_ref,result
assert context['ref_name']==('' if fullsha else ref),result
assert context['ref_type']==('tag' if ref.startswith('deploy-tag-') else 'branch'),result
action=json.loads(pathlib.Path('action-observation.json').read_text())
result['action_env']=action
for key in ['sha','ref','ref_name','ref_type','event_name']:
    assert result['github_env'][key]==context[key],result
    assert action[key]==context[key],result
assert result['fixture']=='deployment-commit-not-default',result
assert context['event_name']==('deployment_status' if s else 'deployment'),result
assert result['workflow_marker'] in ['alpha-at-deployment','beta-at-deployment'],result
if s: assert s['state']!='inactive',result
text=json.dumps(result,sort_keys=True,separators=(',',':'))
print('DEPLOYMENT_E2E_RESULT='+text,flush=True)
with open(os.environ['GITHUB_OUTPUT'],'a') as f: f.write('evidence_hash='+hashlib.sha256(text.encode()).hexdigest()+'\n')
