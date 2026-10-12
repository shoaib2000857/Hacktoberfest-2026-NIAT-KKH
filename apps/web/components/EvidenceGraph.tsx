'use client';
import { useMemo } from 'react';
import { ReactFlow, Background, Controls, MiniMap, type Node, type Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import type { Investigation } from '../lib/types';
export default function EvidenceGraph({caseData,onSelect}:{caseData:Investigation;onSelect:(id:string)=>void}){
 const {nodes,edges}=useMemo(()=>{
  const nodes:Node[]=[],edges:Edge[]=[];
  const offsets:Record<string,number>={};let offset=0;
  caseData.sources.forEach((s,i)=>{offsets[s.id]=offset;nodes.push({id:s.id,position:{x:0,y:offset},data:{label:'SOURCE '+String(i+1).padStart(2,'0')+'\n'+s.filename},className:'graph-source'});offset+=Math.max(1,caseData.claims.filter(c=>c.source_id===s.id).length)*100+70;});
  caseData.claims.forEach(c=>{const local=caseData.claims.filter(x=>x.source_id===c.source_id).findIndex(x=>x.id===c.id);nodes.push({id:c.id,position:{x:340,y:offsets[c.source_id]+local*100},data:{label:c.normalized_summary},className:'graph-claim'});edges.push({id:'contains-'+c.id,source:c.source_id,target:c.id,label:'contains',style:{stroke:'#776650'}});});
  caseData.findings.forEach((f,i)=>{nodes.push({id:f.id,position:{x:720,y:70+i*185},data:{label:f.title},className:'graph-finding'});[f.claim_a_id,f.claim_b_id].forEach(cid=>edges.push({id:f.id+cid,source:cid,target:f.id,label:f.status==='contradiction'?'contradicts':'references',style:{stroke:f.status==='contradiction'?'#C57C70':'#B08D65'}}));});
  return {nodes,edges};
 },[caseData]);
 return <div className="graph-canvas"><ReactFlow nodes={nodes} edges={edges} fitView minZoom={0.25} onNodeClick={(_,node)=>onSelect(node.id)} nodesDraggable nodesConnectable={false} colorMode="dark"><Background color="#47433e" gap={26}/><Controls showInteractive={false}/><MiniMap pannable zoomable nodeColor={n=>n.className==='graph-finding'?'#C57C70':'#B08D65'} maskColor="rgba(23,24,24,.8)"/></ReactFlow><div className="graph-legend"><i/> Source → claim → finding <span>Pan, zoom, or select an evidence node</span></div></div>;
}
