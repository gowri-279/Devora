import type { Module, RepoModule, User } from "./types";

export const users: User[] = [
 {id:"gowri",name:"Gowri",role:"admin",team:"Team Lead",progress:86,avatar:"GW",specialty:"Architecture & Delivery"},
 {id:"ankita",name:"Ankita",role:"developer",team:"Frontend",progress:43,avatar:"AK",specialty:"Frontend Systems"},
 {id:"hemitha",name:"Hemitha",role:"developer",team:"Frontend",progress:52,avatar:"HE",specialty:"UI Engineering"},
 {id:"repodev",name:"Repo Dev",role:"developer",team:"Backend",progress:44,avatar:"RD",specialty:"Repository Parser"},
 {id:"knowledge_eng",name:"Knowledge Eng",role:"developer",team:"Backend",progress:31,avatar:"KE",specialty:"Knowledge Engine"}
];

export const credentials = [
 {id:"gowri",password:"gowri_lead_secure",role:"admin",name:"Gowri · Team Lead"},
 {id:"ankita",password:"dev_ankita_pass",role:"developer",name:"Ankita · Frontend"},
 {id:"hemitha",password:"dev_hemitha_pass",role:"developer",name:"Hemitha · Frontend"},
 {id:"repodev",password:"dev_repodev_pass",role:"developer",name:"Repo Dev · Backend"},
 {id:"knowledge_eng",password:"dev_knowledge_pass",role:"developer",name:"Knowledge Eng · Backend"}
] as const;

export const projectIds = ["payment-service","devora","orders-service"] as const;
export type ProjectId = typeof projectIds[number];

export const projectLabels: Record<ProjectId,string> = {
 "payment-service":"payment-service",
 "devora":"devora",
 "orders-service":"orders-service",
};

export const projectModules: Record<ProjectId, Module[]> = {
 "payment-service": [
  {id:"m1",title:"Project Overview",description:"Understand the project purpose, architecture, services, ownership boundaries and key components.",sources:["README.md","ARCHITECTURE.md"],status:"completed",duration:"18 min",objectives:["Map the repository folders","Identify service boundaries","Trace the local development flow"],code:"git clone <repo>\ncd Devora\ncode .",quiz:[{question:"Which layer is the central controller?",options:["Frontend","FastAPI backend","Knowledge Engine","IBM Bob"],answer:1},{question:"Where should repository parsing happen?",options:["Frontend","Repository Parser","Bob","Browser"],answer:1}]},
  {id:"m2",title:"Local Setup",description:"Set up the development environment and run the project locally before touching integration code.",sources:["LOCAL_SETUP.md","README.md"],status:"current",duration:"20 min",objectives:["Install dependencies","Run the frontend","Start the FastAPI backend"],code:"npm install\nnpm run dev\n# http://localhost:3000",quiz:[{question:"Which command starts the Next.js development server?",options:["npm run dev","npm start-api","python app.py","git run"],answer:0},{question:"Where does the frontend run locally?",options:["localhost:3000","localhost:8000","localhost:5000","localhost:27017"],answer:0}]},
  {id:"m3",title:"API Integration",description:"Explore API contracts, authentication, dashboard routes and the central integration points.",sources:["API.md","openapi.json"],status:"locked",duration:"24 min",objectives:["Read OpenAPI routes","Understand /login and /dashboard","Configure the API base URL"],code:"NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000",quiz:[{question:"Which endpoint authenticates a user?",options:["GET /dashboard","POST /login","POST /ask-bob","GET /analytics"],answer:1},{question:"Who should the frontend call?",options:["MongoDB directly","Repository Parser directly","Backend controller","IBM Bob directly"],answer:2}]},
  {id:"m4",title:"Knowledge Engine",description:"See how project documents and repository knowledge come together to power your personalized learning path.",sources:["KNOWLEDGE_ENGINE.md","INGESTION.md"],status:"locked",duration:"32 min",objectives:["Understand document ingestion","Trace context retrieval","Explain learning-path generation"],code:"POST /upload/documents\nPOST /generate-learning-path",quiz:[{question:"What does the Knowledge Engine primarily process?",options:["UI clicks","Documents and repository metadata","Passwords","Browser cookies"],answer:1},{question:"What is generated for learning?",options:["Random tips","A structured learning path","A database backup","A browser extension"],answer:1}]},
  {id:"m5",title:"Module-Aware Paths",description:"Learn how repository modules such as Auth, Payments, Refunds and Reconciliation become ordered learning units.",sources:["MODULE_MAP.md","LEARNING_PATH.md"],status:"locked",duration:"26 min",objectives:["Understand module discovery","Order prerequisites","Map modules to learning objectives"],code:"modules = [\"Auth\", \"Payments\", \"Refunds\", \"Reconciliation\"]",quiz:[{question:"What should a module-aware path preserve?",options:["Random ordering","Prerequisites and order","Only file names","Only UI labels"],answer:1},{question:"Which is a valid future module?",options:["Reconciliation","Wallpaper","Browser History","Desktop"],answer:0}]},
  {id:"m6",title:"Bob Context",description:"Connect questions to retrieved project context and display grounded answers with confidence and sources.",sources:["BOB_INTEGRATION.md","API.md"],status:"locked",duration:"28 min",objectives:["Trace /ask-bob","Understand context injection","Validate grounded responses"],code:"POST /ask-bob",quiz:[{question:"Who provides retrieved context to Bob?",options:["Knowledge Engine","Browser","MongoDB UI","Developer directly"],answer:0},{question:"What should a grounded answer expose?",options:["Only text","Confidence and reference","Only a score","Nothing"],answer:1}]},
  {id:"m7",title:"Production Readiness",description:"Validate the onboarding checkpoint, identify documentation gaps and prepare the developer for independent delivery.",sources:["RUNBOOK.md","CHECKLIST.md"],status:"locked",duration:"22 min",objectives:["Run the final checklist","Review knowledge gaps","Confirm ownership handoff"],code:"npm run build\n# verify API contracts\n# review unresolved gaps",quiz:[{question:"What indicates a knowledge gap?",options:["Low-confidence grounded answer","A green status","Completed quiz","A loaded logo"],answer:0},{question:"Who can review team knowledge gaps?",options:["Admin","Only Bob","Only browser","Nobody"],answer:0}]}
 ],
 "devora": [
  {id:"d1",title:"Platform Overview",description:"Understand Devora's own architecture: the cockpit UI, the FastAPI backend, the Knowledge Engine and the Bob assistant.",sources:["README.md","ARCHITECTURE.md"],status:"current",duration:"15 min",objectives:["Map the cockpit UI structure","Identify Bob's role","Trace the onboarding data flow"],code:"npm install\nnpm run dev",quiz:[{question:"What does Bob rely on for grounded answers?",options:["Random guesses","Retrieved project context","Browser cache","Hardcoded strings"],answer:1},{question:"Which framework powers the cockpit UI?",options:["Next.js","Django","Rails","Laravel"],answer:0}]},
  {id:"d2",title:"Cockpit UI Architecture",description:"Understand how tabs, shared state and session guarding fit together across the cockpit.",sources:["cockpit.tsx","devora-context.tsx"],status:"locked",duration:"20 min",objectives:["Understand the shared context provider","Trace tab navigation","Identify session guarding"],code:"const {tab,setTab}=useDevora();",quiz:[{question:"Where does cross-tab state live?",options:["The shared context provider","Local component state only","URL params","Cookies"],answer:0},{question:"Which component guards authenticated routes?",options:["Portal","Guard","GlobalBob","SectionTitle"],answer:1}]},
  {id:"d3",title:"Bob Assistant Integration",description:"Learn how Bob's state, thought bubble and chat panel communicate progress without interrupting the user.",sources:["BOB_INTEGRATION.md"],status:"locked",duration:"18 min",objectives:["Understand Bob state transitions","Trace the thought bubble behavior","Explain when the chat should open"],code:"setBobState(\"success\")",quiz:[{question:"When should the full Bob chat panel open?",options:["On every state change","Only on explicit user action","Automatically every 5 seconds","Never"],answer:1},{question:"What communicates Bob's state without opening chat?",options:["A console log","The thought bubble and orb color","A browser alert","A page reload"],answer:1}]},
  {id:"d4",title:"Knowledge Engine",description:"See how project documents and repository knowledge come together to power your personalized learning path.",sources:["KNOWLEDGE_ENGINE.md","INGESTION.md"],status:"locked",duration:"24 min",objectives:["Understand document processing","Trace the retrieval flow","Explain learning-path generation"],code:"POST /upload/documents",quiz:[{question:"What turns documents into searchable chunks?",options:["The ingestion pipeline","The login form","The sidebar","CSS"],answer:0},{question:"What is generated from ingested knowledge?",options:["A learning path","A stylesheet","A cron job","A favicon"],answer:0}]},
  {id:"d5",title:"Progress & Onboarding State",description:"Understand how completed modules are tracked per project and how the learning path advances automatically.",sources:["devora-context.tsx"],status:"locked",duration:"16 min",objectives:["Understand completed-module tracking","Explain per-project module switching","Trace auto-advance on quiz completion"],code:"localStorage.setItem(\"devora_progress_v2\", JSON.stringify(next))",quiz:[{question:"What happens after a module's quiz is completed?",options:["Nothing changes","The next module is selected automatically","The app logs out","The page reloads"],answer:1},{question:"How is progress kept separate per project?",options:["It isn't","Completed modules are stored per project","One global counter","Randomly"],answer:1}]}
 ],
 "orders-service": [
  {id:"o1",title:"Order Intake",description:"Understand how a new order enters the system, gets validated and lands in the intake queue.",sources:["README.md","ORDER_FLOW.md"],status:"current",duration:"16 min",objectives:["Trace order creation","Identify validation steps","Understand the intake queue"],code:"POST /orders",quiz:[{question:"Where does a new order first land?",options:["Intake queue","Refund service","Analytics dashboard","Browser cache"],answer:0},{question:"What validates an incoming order?",options:["Order validation service","CSS","Bob","Nothing"],answer:0}]},
  {id:"o2",title:"Inventory Sync",description:"Learn how stock is reserved and synced so the same item can't be oversold.",sources:["INVENTORY.md"],status:"locked",duration:"20 min",objectives:["Understand stock reservation","Trace sync events","Explain race-condition handling"],code:"POST /inventory/reserve",quiz:[{question:"What prevents overselling stock?",options:["Stock reservation","Random luck","Manual emails","Nothing"],answer:0},{question:"When is inventory synced?",options:["On order intake and fulfillment","Never","Only at midnight","Only manually"],answer:0}]},
  {id:"o3",title:"Fulfillment & Shipping",description:"Trace how a confirmed order moves through warehouse handoff and shipping provider integration.",sources:["FULFILLMENT.md"],status:"locked",duration:"22 min",objectives:["Trace warehouse handoff","Understand shipping provider integration","Explain status updates"],code:"POST /fulfillment/dispatch",quiz:[{question:"Who is notified when an order ships?",options:["The customer via a status update","Nobody","Only the warehouse","Only Bob"],answer:0},{question:"What triggers a fulfillment event?",options:["A confirmed, in-stock order","A page refresh","A login","A CSS change"],answer:0}]},
  {id:"o4",title:"Cancellations & Returns",description:"Understand cancellation windows and how an approved return flows back into inventory and refunds.",sources:["RETURNS.md"],status:"locked",duration:"18 min",objectives:["Understand cancellation windows","Trace the return-to-refund handoff","Explain inventory restock"],code:"POST /orders/{id}/cancel",quiz:[{question:"What happens to inventory after an approved return?",options:["It is restocked","It is deleted","Nothing","It's donated automatically"],answer:0},{question:"What service does a return eventually notify?",options:["The payments/refunds service","The login screen","The favicon","CSS"],answer:0}]},
  {id:"o5",title:"Order Analytics & SLAs",description:"Learn how order SLAs are tracked and how on-call should respond to at-risk orders.",sources:["ANALYTICS.md","RUNBOOK.md"],status:"locked",duration:"20 min",objectives:["Understand SLA tracking","Trace late-order alerts","Review the on-call runbook"],code:"GET /orders/analytics",quiz:[{question:"What flags an order at risk of breaching SLA?",options:["The analytics/SLA monitor","A browser popup","Bob randomly","Nothing"],answer:0},{question:"Where should on-call check first for order incidents?",options:["The runbook","Social media","A whiteboard","Nowhere"],answer:0}]}
 ]
};

export const projectRepo: Record<ProjectId,{url:string; modules:RepoModule[]}> = {
 "payment-service": {
  url:"https://github.com/acme/payment-service",
  modules:[
   {name:"Authentication",path:"backend/auth",files:["AuthMiddleware.ts","JwtService.ts"],tech:"JWT · FastAPI"},
   {name:"Payments",path:"backend/payments",files:["PaymentService.ts","PaymentController.ts"],tech:"TypeScript · SQL"},
   {name:"Refunds",path:"backend/refunds",files:["RefundService.ts"],tech:"TypeScript"},
   {name:"Reconciliation",path:"backend/reconciliation",files:["RetryWorker.ts","KafkaConsumer.ts"],tech:"Kafka · Worker"}
  ]
 },
 "devora": {
  url:"https://github.com/acme/devora",
  modules:[
   {name:"Cockpit UI",path:"frontend/components",files:["cockpit.tsx","devora-context.tsx"],tech:"Next.js · React"},
   {name:"Bob Assistant",path:"backend/bob",files:["BobController.ts","ContextRetriever.ts"],tech:"TypeScript · LLM"},
   {name:"Knowledge Engine",path:"backend/knowledge-engine",files:["Ingestion.ts","Embeddings.ts"],tech:"Python · Vector DB"},
   {name:"Session Guard",path:"frontend/components",files:["guard.tsx","session-provider.tsx"],tech:"React · JWT"}
  ]
 },
 "orders-service": {
  url:"https://github.com/acme/orders-service",
  modules:[
   {name:"Order Intake",path:"backend/orders",files:["OrderController.ts","OrderValidator.ts"],tech:"TypeScript · SQL"},
   {name:"Inventory",path:"backend/inventory",files:["InventoryService.ts","StockReserver.ts"],tech:"TypeScript · Redis"},
   {name:"Fulfillment",path:"backend/fulfillment",files:["FulfillmentWorker.ts","ShippingClient.ts"],tech:"Worker · Kafka"},
   {name:"Returns",path:"backend/returns",files:["ReturnService.ts"],tech:"TypeScript"}
  ]
 }
};

export const broadcasts = [
 {id:"n1",audience:"All",time:"09:42",title:"Sprint checkpoint",body:"Local Setup and API Integration are the team focus today. Use Bob for documentation-grounded questions."},
 {id:"n2",audience:"Frontend Developers",time:"Yesterday",title:"UI contract freeze",body:"Keep API client changes isolated to the frontend adapter until the backend merge."},
 {id:"n3",audience:"Backend Developers",time:"Yesterday",title:"Parser handoff",body:"Repository parser output should remain structured JSON and flow through the central controller."}
];

export const knowledgeGaps = [
 {question:"How does reconciliation retry work?",count:5,status:"Open"},
 {question:"Where is Kafka configured?",count:3,status:"Open"},
 {question:"Which service owns refund state?",count:2,status:"Review"},
 {question:"What is the production ingestion schedule?",count:2,status:"Open"}
];
