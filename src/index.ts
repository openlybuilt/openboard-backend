import { createClerkClient } from '@clerk/backend';

interface Env {
 DB: D1Database;
 CLERK_SECRET_KEY: string;
 CLERK_PUBLISHABLE_KEY: string;
 FRONTEND_ORIGIN: string;
}

const MAX_BODY_BYTES=2_000_000;
const TRASH_RETENTION_MS=30*24*60*60*1000;
const ID=/^[a-zA-Z0-9_-]{1,100}$/;

async function purgeExpiredBoards(env:Env,now=Date.now()) {
 await env.DB.prepare('DELETE FROM boards WHERE deleted_at IS NOT NULL AND deleted_at <= ?').bind(now-TRASH_RETENTION_MS).run();
}

export default {
 async scheduled(_controller:ScheduledController,env:Env):Promise<void> {
  await purgeExpiredBoards(env);
 },
 async fetch(request:Request,env:Env):Promise<Response> {
  const origin=request.headers.get('Origin');
  const cors=new Headers({'Vary':'Origin','Access-Control-Allow-Methods':'GET, PUT, DELETE, OPTIONS','Access-Control-Allow-Headers':'Authorization, Content-Type'});
  if(origin===env.FRONTEND_ORIGIN)cors.set('Access-Control-Allow-Origin',origin);
  const reply=(body:unknown,status=200)=>Response.json(body,{status,headers:cors});
  if(origin&&origin!==env.FRONTEND_ORIGIN)return reply({error:'Origin not allowed'},403);
  if(request.method==='OPTIONS')return new Response(null,{status:204,headers:cors});
  const path=new URL(request.url).pathname;
  if(path==='/health'&&request.method==='GET')return reply({ok:true});
  if(!env.CLERK_SECRET_KEY||!env.CLERK_PUBLISHABLE_KEY||!env.FRONTEND_ORIGIN)return reply({error:'Server not configured'},503);
  try{
   const clerk=createClerkClient({secretKey:env.CLERK_SECRET_KEY,publishableKey:env.CLERK_PUBLISHABLE_KEY});
   const auth=await clerk.authenticateRequest(request,{authorizedParties:[env.FRONTEND_ORIGIN]});
   if(!auth.isSignedIn)return reply({error:'Sign in required'},401);
   const userId=auth.toAuth().userId;
   if(!userId)return reply({error:'Sign in required'},401);
   if(path==='/boards'&&request.method==='GET'){
    const result=await env.DB.prepare('SELECT body FROM boards WHERE owner_id = ? AND (deleted_at IS NULL OR deleted_at > ?) ORDER BY updated_at DESC').bind(userId,Date.now()-TRASH_RETENTION_MS).all<{body:string}>();
    return reply({boards:result.results.map(row=>JSON.parse(row.body))});
   }
   const match=path.match(/^\/boards\/([a-zA-Z0-9_-]{1,100})$/);
   if(!match)return reply({error:'Not found'},404);
   const id=match[1];
   if(request.method==='DELETE'){
    await env.DB.prepare('DELETE FROM boards WHERE owner_id = ? AND id = ?').bind(userId,id).run();
    return new Response(null,{status:204,headers:cors});
   }
   if(request.method==='PUT'){
    const body=await request.text();
    if(new TextEncoder().encode(body).byteLength>MAX_BODY_BYTES)return reply({error:'Board is too large'},413);
    let board:Record<string,unknown>;
    try{board=JSON.parse(body)}catch{return reply({error:'Invalid JSON'},400)}
    if(!board||Array.isArray(board)||typeof board!=='object'||board.id!==id||!ID.test(id)||typeof board.name!=='string'||board.name.length>100||typeof board.updatedAt!=='number'||!Number.isFinite(board.updatedAt)||!Array.isArray(board.nodes)||!Array.isArray(board.edges))return reply({error:'Invalid board'},400);
    const deletedAt=board.deletedAt;
    if(deletedAt!==undefined&&(typeof deletedAt!=='number'||!Number.isFinite(deletedAt)||deletedAt>Date.now()+60_000||deletedAt<=Date.now()-TRASH_RETENTION_MS))return reply({error:'Invalid deletion date'},400);
    await env.DB.prepare('INSERT INTO boards(owner_id,id,body,updated_at,deleted_at) VALUES(?,?,?,?,?) ON CONFLICT(owner_id,id) DO UPDATE SET body=excluded.body,updated_at=excluded.updated_at,deleted_at=excluded.deleted_at').bind(userId,id,body,board.updatedAt,deletedAt??null).run();
    return reply({ok:true});
   }
   return reply({error:'Method not allowed'},405);
  }catch(error){
   console.error('Request failed',error instanceof Error?error.name:'unknown');
   return reply({error:'Request failed'},500);
  }
 },
};
