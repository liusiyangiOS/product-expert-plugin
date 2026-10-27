import hashlib,json,pathlib,tempfile,subprocess
root=pathlib.Path(tempfile.mkdtemp(prefix='product-graph-qa-'))
(root/'research.md').write_text('合成访谈记录：部分用户不理解入口',encoding='utf8')
sha=hashlib.sha256((root/'research.md').read_bytes()).hexdigest()
sources=[dict(id='local',kind='file',ref='research.md',version='sha256:'+sha),dict(id='remote',kind='url',ref='https://example.invalid/research',version='2026-10-27')]
nodes=[dict(id=i,type=t,label=i,sources=s,status=st) for i,t,s,st in [('evidence','evidence',['local'],'unverified'),('counter','evidence',['remote'],'unverified'),('hyp','hypothesis',[],'unverified'),('req','requirement',[],'draft'),('design','design',[],'draft'),('accept','acceptance',[],'planned')]]
edges=[dict(zip(('from','to','relation','basis','sources'),x)) for x in [('evidence','hyp','supports','observed',['local']),('counter','hyp','challenges','hypothesis',['remote']),('hyp','req','motivates','hypothesis',[]),('req','design','realized_by','inferred',[]),('design','accept','verified_by','inferred',[])]]
def task(i,deps,status,evidence=[]): return dict(id=i,depends_on=deps,owner='qa',write_scope=['docs/'+i],status=status,acceptance=['观察结果'],evidence=evidence)
tasks=[task('blocked',[],'blocked'),task('intermediate',['blocked'],'done',['先前记录']),task('downstream',['intermediate'],'pending'),task('independent',[],'pending')]
graph=dict(schema_version=1,sources=sources,nodes=nodes,edges=edges,tasks=tasks)
graphpath=root/'graph.json'; graphpath.write_text(json.dumps(graph,ensure_ascii=False),encoding='utf8')
tool='/Users/liusiyang/Documents/GitHubOfMine/product-expert-plugin/packages/codex/skills/product-shared/product_graph.py'
def run(name,args):
 p=subprocess.run(['python3',tool,*args],capture_output=True,text=True); (root/(name+'.json')).write_text(p.stdout,encoding='utf8'); print(name,'exit',p.returncode,'stdout',p.stdout.strip(),'stderr',p.stderr.strip()); return p.returncode,json.loads(p.stdout)
print('evidence_dir',root)
c,v=run('validate',['validate',str(graphpath)]); assert c==0 and v['ok']
c,v=run('impact',['impact',str(graphpath),'evidence']); assert c==0 and v['nodes']==['evidence','hyp','req','design','accept'] and v['triggers'][1]['basis']=='hypothesis'
c,v=run('counter',['impact',str(graphpath),'counter']); assert c==0 and v['triggers'][0]['relation']=='challenges'
c,v=run('ready',['ready',str(graphpath)]); assert c==0 and v['ready']==['independent']
c,v=run('initial',['check-files',str(graphpath),'--root',str(root)]); assert c==2 and len(v['local_verified'])==1 and len(v['remote_unverified'])==1
(root/'research.md').write_text('合成记录已改变：反例出现',encoding='utf8')
c,v=run('changed',['check-files',str(graphpath),'--root',str(root)]); assert c==2 and v['changed'][0]['id']=='local' and {'req','design','accept'} <= set(v['impacts'][0]['paths'][0]['nodes'])
print('SCENARIO_ASSERTIONS=PASS')
