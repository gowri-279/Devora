import type { Module, User } from "./types";

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

export const modules: Module[] = [
 {id:"m1",title:"Project Overview",description:"Understand the project purpose, architecture, services, ownership boundaries and key components.",sources:["README.md","ARCHITECTURE.md"],status:"completed",duration:"18 min",objectives:["Map the repository folders","Identify service boundaries","Trace the local development flow"],code:"git clone <repo>\ncd Devora\ncode .",quiz:[{question:"Which layer is the central controller?",options:["Frontend","FastAPI backend","Knowledge Engine","IBM Bob"],answer:1},{question:"Where should repository parsing happen?",options:["Frontend","Repository Parser","Bob","Browser"],answer:1}]},
 {id:"m2",title:"Local Setup",description:"Set up the development environment and run the project locally before touching integration code.",sources:["LOCAL_SETUP.md","README.md"],status:"current",duration:"20 min",objectives:["Install dependencies","Run the frontend","Start the FastAPI backend"],code:"npm install\nnpm run dev\n# http://localhost:3000",quiz:[{question:"Which command starts the Next.js development server?",options:["npm run dev","npm start-api","python app.py","git run"],answer:0},{question:"Where does the frontend run locally?",options:["localhost:3000","localhost:8000","localhost:5000","localhost:27017"],answer:0}]},
 {id:"m3",title:"API Integration",description:"Explore API contracts, authentication, dashboard routes and the central integration points.",sources:["API.md","openapi.json"],status:"locked",duration:"24 min",objectives:["Read OpenAPI routes","Understand /login and /dashboard","Configure the API base URL"],code:"NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000",quiz:[{question:"Which endpoint authenticates a user?",options:["GET /dashboard","POST /login","POST /ask-bob","GET /analytics"],answer:1},{question:"Who should the frontend call?",options:["MongoDB directly","Repository Parser directly","Backend controller","IBM Bob directly"],answer:2}]},
 {id:"m4",title:"Knowledge Engine",description:"Follow documents and repository metadata through ingestion, chunking, embeddings and learning-path generation.",sources:["KNOWLEDGE_ENGINE.md","INGESTION.md"],status:"locked",duration:"32 min",objectives:["Understand document ingestion","Trace context retrieval","Explain learning-path generation"],code:"POST /upload/documents\nPOST /generate-learning-path",quiz:[{question:"What does the Knowledge Engine primarily process?",options:["UI clicks","Documents and repository metadata","Passwords","Browser cookies"],answer:1},{question:"What is generated for learning?",options:["Random tips","A structured learning path","A database backup","A browser extension"],answer:1}]},
 {id:"m5",title:"Module-Aware Paths",description:"Learn how repository modules such as Auth, Payments, Refunds and Reconciliation become ordered learning units.",sources:["MODULE_MAP.md","LEARNING_PATH.md"],status:"locked",duration:"26 min",objectives:["Understand module discovery","Order prerequisites","Map modules to learning objectives"],code:"modules = [\"Auth\", \"Payments\", \"Refunds\", \"Reconciliation\"]",quiz:[{question:"What should a module-aware path preserve?",options:["Random ordering","Prerequisites and order","Only file names","Only UI labels"],answer:1},{question:"Which is a valid future module?",options:["Reconciliation","Wallpaper","Browser History","Desktop"],answer:0}]},
 {id:"m6",title:"Bob Context",description:"Connect questions to retrieved project context and display grounded answers with confidence and sources.",sources:["BOB_INTEGRATION.md","API.md"],status:"locked",duration:"28 min",objectives:["Trace /ask-bob","Understand context injection","Validate grounded responses"],code:"POST /ask-bob",quiz:[{question:"Who provides retrieved context to Bob?",options:["Knowledge Engine","Browser","MongoDB UI","Developer directly"],answer:0},{question:"What should a grounded answer expose?",options:["Only text","Confidence and reference","Only a score","Nothing"],answer:1}]},
 {id:"m7",title:"Production Readiness",description:"Validate the onboarding checkpoint, identify documentation gaps and prepare the developer for independent delivery.",sources:["RUNBOOK.md","CHECKLIST.md"],status:"locked",duration:"22 min",objectives:["Run the final checklist","Review knowledge gaps","Confirm ownership handoff"],code:"npm run build\n# verify API contracts\n# review unresolved gaps",quiz:[{question:"What indicates a knowledge gap?",options:["Low-confidence grounded answer","A green status","Completed quiz","A loaded logo"],answer:0},{question:"Who can review team knowledge gaps?",options:["Admin","Only Bob","Only browser","Nobody"],answer:0}]}
];

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
