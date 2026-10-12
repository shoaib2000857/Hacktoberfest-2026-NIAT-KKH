export type Source = { id:string; filename:string; mime_type:string; sha256:string; uploaded_at:string; published_at:string|null; version_group:string|null; extracted_text:string; extraction_status:string; sequence_index:number };
export type Claim = {id:string;source_id:string;category:string;subject:string;predicate:string;value:string|number|null;currency:string|null;unit:string|null;modality:string;conditions:string[];original_text:string;normalized_summary:string;page_number:number|null;location_quality:string};
export type Finding = {id:string;claim_a_id:string;claim_b_id:string;category:string;status:string;severity:string;title:string;explanation:string;validation_method:string;evidence_verified:boolean;limitations:string[];review_status:string;review_notes:string};
export type Investigation = {id:string;title:string;description:string;status:string;stage:string;created_at:string;updated_at:string;sources:Source[];claims:Claim[];findings:Finding[];model_identifier:string|null;error_message:string|null;is_example?:boolean;analysis_completed_at?:string};
export type Summary = Omit<Investigation,'sources'|'claims'|'findings'> & {source_count:number;finding_count:number};
export async function api<T>(path:string,init?:RequestInit):Promise<T> {
 const response=await fetch('/api/v1'+path,init);
 if(!response.ok){let message='The request could not be completed.';try{const body=await response.json();message=typeof body.detail==='string'?body.detail:JSON.stringify(body.detail);}catch{}throw new Error(message);}
 if(response.status===204)return undefined as T;
 return response.json();
}
export const json = (body:unknown,method='POST'):RequestInit => ({method,headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
export const label=(text:string)=>text.replaceAll('_',' ');
