'use client';
import { useMemo,useState } from 'react';
import { ReactFlow, Background, Controls, MiniMap, type Node, type Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {label,type Investigation} from '../lib/types';
export default function EvidenceGraph({caseData,onSelect}:{caseData:Investigation;onSelect:(id:string)=>void}){
 const [filter,setFilter]=useState('all'),[focus,setFocus]=useState<string|null>(null);
 const {nodes,edges,connected}=useMemo(()=>{
  const nodes:Node[]=[],edges:Edge[]=[];
  const findings=caseData.findings.filter(f=>filter==='all'||f.status===filter);
  const claimIds=new Set(findings.flatMap(f=>[f.claim_a_id,f.claim_b_id]));
  const claims=caseData.claims.filter(c=>filter==='all'||claimIds.has(c.id));
  const sourceIds=new Set(claims.map(c=>c.source_id));
  const offsets:Record<string,number>={};let offset=0;
  caseData.sources.filter(s=>filter==='all'||sourceIds.has(s.id)).forEach((s,i)=>{offsets[s.id]=offset;nodes.push({id:s.id,position:{x:0,y:offset},data:{label:'SOURCE '+String(i+1).padStart(2,'0')+'\n'+s.filename},className:'graph-source'});offset+=Math.max(1,claims.filter(c=>c.source_id===s.id).length)*100+70;});
  claims.forEach(c=>{const local=claims.filter(x=>x.source_id===c.source_id).findIndex(x=>x.id===c.id);nodes.push({id:c.id,position:{x:340,y:offsets[c.source_id]+local*100},data:{label:c.normalized_summary},className:'graph-claim'});edges.push({id:'contains-'+c.id,source:c.source_id,target:c.id,label:'contains claim',style:{stroke:'#776650'}});});
  findings.forEach((f,i)=>{nodes.push({id:f.id,position:{x:720,y:70+i*185},data:{label:f.title},className:'graph-finding'});const relation={contradiction:'contradicts',changed_term:'updates',material_qualification:'qualifies',missing_disclosure:'qualifies'}[f.status]||'references';[f.claim_a_id,f.claim_b_id].forEach(cid=>edges.push({id:f.id+cid,source:cid,target:f.id,label:relation,style:{stroke:f.status==='contradiction'?'#C57C70':'#B08D65'}}));});
  const connected=new Set<string>();
  if(focus){connected.add(focus);edges.filter(e=>e.source===focus||e.target===focus).forEach(e=>{connected.add(e.source);connected.add(e.target);});const f=findings.find(f=>f.id===focus);if(f)claims.filter(c=>[f.claim_a_id,f.claim_b_id].includes(c.id)).forEach(c=>connected.add(c.source_id));}
  nodes.forEach(n=>{if(focus)n.className+=' '+(connected.has(n.id)?'graph-focus':'graph-dim');});
  edges.forEach(e=>{if(focus&&!connected.has(e.source))e.style={...e.style,opacity:.15};});
  return {nodes,edges,connected};
 },[caseData,filter,focus]);
 const source=caseData.sources.find(s=>s.id===focus),claim=caseData.claims.find(c=>c.id===focus),finding=caseData.findings.find(f=>f.id===focus);
 return <><div className="graph-controls"><label>Finding filter <select value={filter} onChange={e=>{setFilter(e.target.value);setFocus(null);}}><option value="all">All evidence</option>{[...new Set(caseData.findings.map(f=>f.status))].map(s=><option key={s} value={s}>{label(s)}</option>)}</select></label><button className="text-button" onClick={()=>setFocus(null)}>Clear selection</button></div><div className="graph-canvas"><ReactFlow key={filter} nodes={nodes} edges={edges} fitView minZoom={0.25} onNodeClick={(_,node)=>setFocus(node.id)} nodesDraggable nodesConnectable={false} colorMode="dark"><Background color="#47433e" gap={26}/><Controls showInteractive={false}/><MiniMap pannable zoomable nodeColor={n=>n.className?.includes('graph-finding')?'#C57C70':'#B08D65'} maskColor="rgba(23,24,24,.8)"/></ReactFlow><div className="graph-legend"><i/> Source → claim → finding <span>Select to highlight related evidence</span></div></div>{focus&&<div className="graph-details"><span className="eyebrow">SELECTED EVIDENCE · {connected.size} CONNECTED NODES</span><h3>{source?.filename||claim?.normalized_summary||finding?.title}</h3><p className="muted">{source?'SHA-256: '+source.sha256:claim?claim.original_text:finding?.explanation}</p><button className="secondary" onClick={()=>onSelect(focus)}>Open evidence details</button></div>}</>;
}
