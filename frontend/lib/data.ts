import type { RepoModule, User } from "./types";

// Legacy per-project content used only as the source for the local learning-path
// fallback (see lib/learningPath.ts) when no backend is configured or reachable.
type LegacyModule = {
  id: string;
  title: string;
  description: string;
  sources: string[];
  status: string;
  duration: string;
  objectives: string[];
  code: string;
  quiz: {
    question: string;
    options: string[];
    answer: number;
    hint?: string;
  }[];
};

export const users: User[] = [
  {
    id: "gowri",
    name: "Gowri",
    role: "admin",
    team: "Team Lead",
    progress: 86,
    avatar: "GW",
    specialty: "Architecture & Delivery",
  },
  {
    id: "ankita",
    name: "Ankita",
    role: "developer",
    team: "Frontend",
    progress: 43,
    avatar: "AK",
    specialty: "Frontend Systems",
  },
  {
    id: "hemitha",
    name: "Hemitha",
    role: "developer",
    team: "Frontend",
    progress: 52,
    avatar: "HE",
    specialty: "UI Engineering",
  },
  {
    id: "repodev",
    name: "Repo Dev",
    role: "developer",
    team: "Backend",
    progress: 44,
    avatar: "RD",
    specialty: "Repository Parser",
  },
  {
    id: "knowledge_eng",
    name: "Knowledge Eng",
    role: "developer",
    team: "Backend",
    progress: 31,
    avatar: "KE",
    specialty: "Knowledge Engine",
  },
];

export const credentials = [
  {
    id: "gowri",
    password: "gowri_lead_secure",
    role: "admin",
    name: "Gowri · Team Lead",
  },
  {
    id: "ankita",
    password: "dev_ankita_pass",
    role: "developer",
    name: "Ankita · Frontend",
  },
  {
    id: "hemitha",
    password: "dev_hemitha_pass",
    role: "developer",
    name: "Hemitha · Frontend",
  },
  {
    id: "repodev",
    password: "dev_repodev_pass",
    role: "developer",
    name: "Repo Dev · Backend",
  },
  {
    id: "knowledge_eng",
    password: "dev_knowledge_pass",
    role: "developer",
    name: "Knowledge Eng · Backend",
  },
] as const;


// ============================================================
// PROJECTS
// ============================================================

export const projectIds = [
  "fastapi",
  "devora",
  "orders-service",
] as const;

export type ProjectId = typeof projectIds[number];

export const projectLabels: Record<ProjectId, string> = {
  fastapi: "FastAPI",
  devora: "Devora",
  "orders-service": "orders-service",
};


// ============================================================
// LEGACY FALLBACK LEARNING MODULES
// ============================================================

export const projectModules: Record<ProjectId, LegacyModule[]> = {
  fastapi: [
    {
      id: "m1",
      title: "Project Overview",
      description:
        "Understand the project purpose, architecture, services, ownership boundaries and key components.",
      sources: ["README.md", "ARCHITECTURE.md"],
      status: "completed",
      duration: "18 min",
      objectives: [
        "Map the repository folders",
        "Identify service boundaries",
        "Trace the local development flow",
      ],
      code: "git clone https://github.com/tiangolo/fastapi\ncd fastapi",
      quiz: [
        {
          question: "Which layer is the central controller?",
          options: [
            "Frontend",
            "FastAPI backend",
            "Knowledge Engine",
            "IBM Bob",
          ],
          answer: 1,
        },
        {
          question: "Where should repository parsing happen?",
          options: [
            "Frontend",
            "Repository Parser",
            "Bob",
            "Browser",
          ],
          answer: 1,
        },
      ],
    },

    {
      id: "m2",
      title: "Local Setup",
      description:
        "Set up the development environment and run the FastAPI project locally before touching integration code.",
      sources: ["README.md"],
      status: "current",
      duration: "20 min",
      objectives: [
        "Install dependencies",
        "Understand the FastAPI development environment",
        "Run the project locally",
      ],
      code: "git clone https://github.com/tiangolo/fastapi\ncd fastapi",
      quiz: [
        {
          question: "What framework is this repository primarily built around?",
          options: [
            "Next.js",
            "FastAPI",
            "Django",
            "Rails",
          ],
          answer: 1,
        },
        {
          question: "What is the purpose of the repository?",
          options: [
            "A FastAPI web framework",
            "A payment service",
            "A frontend dashboard",
            "A database",
          ],
          answer: 0,
        },
      ],
    },

    {
      id: "m3",
      title: "API Integration",
      description:
        "Explore API contracts, routing, request handling and the central integration points.",
      sources: ["README.md", "docs"],
      status: "locked",
      duration: "24 min",
      objectives: [
        "Understand API routes",
        "Trace request handling",
        "Understand FastAPI application structure",
      ],
      code: "from fastapi import FastAPI\n\napp = FastAPI()",
      quiz: [
        {
          question: "Which framework powers the repository?",
          options: [
            "FastAPI",
            "React",
            "Spring",
            "Laravel",
          ],
          answer: 0,
        },
        {
          question: "What does an API route define?",
          options: [
            "How a request is handled",
            "A CSS animation",
            "A database backup",
            "A browser cookie",
          ],
          answer: 0,
        },
      ],
    },

    {
      id: "m4",
      title: "Dependencies",
      description:
        "Understand the project's dependency structure and how its components rely on one another.",
      sources: ["pyproject.toml", "requirements"],
      status: "locked",
      duration: "32 min",
      objectives: [
        "Understand project dependencies",
        "Trace dependency relationships",
        "Identify important framework components",
      ],
      code: "pip install fastapi",
      quiz: [
        {
          question: "What does a dependency provide?",
          options: [
            "Reusable functionality",
            "Only UI styling",
            "Browser history",
            "Nothing",
          ],
          answer: 0,
        },
      ],
    },

    {
      id: "m5",
      title: "Middleware",
      description:
        "Learn how middleware participates in request processing and how cross-cutting behavior is handled.",
      sources: ["middleware", "docs"],
      status: "locked",
      duration: "26 min",
      objectives: [
        "Understand middleware",
        "Trace request processing",
        "Identify cross-cutting concerns",
      ],
      code: "app.add_middleware(...)",
      quiz: [
        {
          question: "What is middleware used for?",
          options: [
            "Processing requests and responses",
            "Drawing UI components",
            "Storing passwords",
            "Managing Git branches",
          ],
          answer: 0,
        },
      ],
    },

    {
      id: "m6",
      title: "OpenAPI & Security",
      description:
        "Understand API documentation, OpenAPI generation and security-related components.",
      sources: ["openapi", "security"],
      status: "locked",
      duration: "28 min",
      objectives: [
        "Understand OpenAPI",
        "Trace API documentation",
        "Understand security mechanisms",
      ],
      code: "app.openapi()",
      quiz: [
        {
          question: "What does OpenAPI describe?",
          options: [
            "API structure and contracts",
            "CSS styles",
            "Git commits",
            "Operating-system processes",
          ],
          answer: 0,
        },
      ],
    },

    {
      id: "m7",
      title: "Production Readiness",
      description:
        "Validate the repository architecture, identify documentation gaps and prepare for independent development.",
      sources: ["README.md", "docs"],
      status: "locked",
      duration: "22 min",
      objectives: [
        "Review the repository structure",
        "Identify knowledge gaps",
        "Validate the development workflow",
      ],
      code: "pytest\n# validate repository behavior",
      quiz: [
        {
          question: "What indicates a knowledge gap?",
          options: [
            "Low-confidence grounded answer",
            "A green status",
            "Completed quiz",
            "A loaded logo",
          ],
          answer: 0,
        },
      ],
    },
  ],

  devora: [
    {
      id: "d1",
      title: "Platform Overview",
      description:
        "Understand Devora's own architecture: the cockpit UI, the FastAPI backend, the Knowledge Engine and the Bob assistant.",
      sources: ["README.md", "ARCHITECTURE.md"],
      status: "current",
      duration: "15 min",
      objectives: [
        "Map the cockpit UI structure",
        "Identify Bob's role",
        "Trace the onboarding data flow",
      ],
      code: "npm install\nnpm run dev",
      quiz: [
        {
          question: "What does Bob rely on for grounded answers?",
          options: [
            "Random guesses",
            "Retrieved project context",
            "Browser cache",
            "Hardcoded strings",
          ],
          answer: 1,
        },
        {
          question: "Which framework powers the cockpit UI?",
          options: [
            "Next.js",
            "Django",
            "Rails",
            "Laravel",
          ],
          answer: 0,
        },
      ],
    },

    {
      id: "d2",
      title: "Cockpit UI Architecture",
      description:
        "Understand how tabs, shared state and session guarding fit together across the cockpit.",
      sources: ["cockpit.tsx", "devora-context.tsx"],
      status: "locked",
      duration: "20 min",
      objectives: [
        "Understand the shared context provider",
        "Trace tab navigation",
        "Identify session guarding",
      ],
      code: 'const {tab,setTab}=useDevora();',
      quiz: [
        {
          question: "Where does cross-tab state live?",
          options: [
            "The shared context provider",
            "Local component state only",
            "URL params",
            "Cookies",
          ],
          answer: 0,
        },
      ],
    },

    {
      id: "d3",
      title: "Bob Assistant Integration",
      description:
        "Learn how Bob's state, thought bubble and chat panel communicate progress without interrupting the user.",
      sources: ["BOB_INTEGRATION.md"],
      status: "locked",
      duration: "18 min",
      objectives: [
        "Understand Bob state transitions",
        "Trace the thought bubble behavior",
        "Explain when the chat should open",
      ],
      code: 'setBobState("success")',
      quiz: [
        {
          question: "When should the full Bob chat panel open?",
          options: [
            "On every state change",
            "Only on explicit user action",
            "Automatically every 5 seconds",
            "Never",
          ],
          answer: 1,
        },
      ],
    },

    {
      id: "d4",
      title: "Knowledge Engine",
      description:
        "See how project documents and repository knowledge come together to power your personalized learning path.",
      sources: ["KNOWLEDGE_ENGINE.md", "INGESTION.md"],
      status: "locked",
      duration: "24 min",
      objectives: [
        "Understand document processing",
        "Trace the retrieval flow",
        "Explain learning-path generation",
      ],
      code: "POST /upload/documents",
      quiz: [
        {
          question: "What turns documents into searchable chunks?",
          options: [
            "The ingestion pipeline",
            "The login form",
            "The sidebar",
            "CSS",
          ],
          answer: 0,
        },
      ],
    },

    {
      id: "d5",
      title: "Progress & Onboarding State",
      description:
        "Understand how completed modules are tracked per project and how the learning path advances automatically.",
      sources: ["devora-context.tsx"],
      status: "locked",
      duration: "16 min",
      objectives: [
        "Understand completed-module tracking",
        "Explain per-project module switching",
        "Trace auto-advance on quiz completion",
      ],
      code:
        'localStorage.setItem("devora_progress_v2", JSON.stringify(next))',
      quiz: [
        {
          question: "What happens after a module's quiz is completed?",
          options: [
            "Nothing changes",
            "The next module is selected automatically",
            "The app logs out",
            "The page reloads",
          ],
          answer: 1,
        },
      ],
    },
  ],

  "orders-service": [
    {
      id: "o1",
      title: "Order Intake",
      description:
        "Understand how a new order enters the system, gets validated and lands in the intake queue.",
      sources: ["README.md", "ORDER_FLOW.md"],
      status: "current",
      duration: "16 min",
      objectives: [
        "Trace order creation",
        "Identify validation steps",
        "Understand the intake queue",
      ],
      code: "POST /orders",
      quiz: [
        {
          question: "Where does a new order first land?",
          options: [
            "Intake queue",
            "Refund service",
            "Analytics dashboard",
            "Browser cache",
          ],
          answer: 0,
        },
      ],
    },

    {
      id: "o2",
      title: "Inventory Sync",
      description:
        "Learn how stock is reserved and synced so the same item can't be oversold.",
      sources: ["INVENTORY.md"],
      status: "locked",
      duration: "20 min",
      objectives: [
        "Understand stock reservation",
        "Trace sync events",
        "Explain race-condition handling",
      ],
      code: "POST /inventory/reserve",
      quiz: [
        {
          question: "What prevents overselling stock?",
          options: [
            "Stock reservation",
            "Random luck",
            "Manual emails",
            "Nothing",
          ],
          answer: 0,
        },
      ],
    },

    {
      id: "o3",
      title: "Fulfillment & Shipping",
      description:
        "Trace how a confirmed order moves through warehouse handoff and shipping provider integration.",
      sources: ["FULFILLMENT.md"],
      status: "locked",
      duration: "22 min",
      objectives: [
        "Trace warehouse handoff",
        "Understand shipping provider integration",
        "Explain status updates",
      ],
      code: "POST /fulfillment/dispatch",
      quiz: [
        {
          question: "What triggers a fulfillment event?",
          options: [
            "A confirmed, in-stock order",
            "A page refresh",
            "A login",
            "A CSS change",
          ],
          answer: 0,
        },
      ],
    },

    {
      id: "o4",
      title: "Cancellations & Returns",
      description:
        "Understand cancellation windows and how an approved return flows back into inventory and refunds.",
      sources: ["RETURNS.md"],
      status: "locked",
      duration: "18 min",
      objectives: [
        "Understand cancellation windows",
        "Trace the return-to-refund handoff",
        "Explain inventory restock",
      ],
      code: "POST /orders/{id}/cancel",
      quiz: [
        {
          question: "What happens to inventory after an approved return?",
          options: [
            "It is restocked",
            "It is deleted",
            "Nothing",
            "It's donated automatically",
          ],
          answer: 0,
        },
      ],
    },

    {
      id: "o5",
      title: "Order Analytics & SLAs",
      description:
        "Learn how order SLAs are tracked and how on-call should respond to at-risk orders.",
      sources: ["ANALYTICS.md", "RUNBOOK.md"],
      status: "locked",
      duration: "20 min",
      objectives: [
        "Understand SLA tracking",
        "Trace late-order alerts",
        "Review the on-call runbook",
      ],
      code: "GET /orders/analytics",
      quiz: [
        {
          question: "Where should on-call check first for order incidents?",
          options: [
            "The runbook",
            "Social media",
            "A whiteboard",
            "Nowhere",
          ],
          answer: 0,
        },
      ],
    },
  ],
};


// ============================================================
// REPOSITORY INFORMATION
// ============================================================

export const projectRepo: Record<
  ProjectId,
  { url: string; modules: RepoModule[] }
> = {
  fastapi: {
    url: "https://github.com/tiangolo/fastapi",

    // These are currently UI/display modules.
    // The actual repository-aware learning path comes from KE.
    modules: [
      {
        name: "FastAPI",
        path: "fastapi",
        files: ["README.md"],
        tech: "Python · FastAPI",
      },
      {
        name: "Dependencies",
        path: "fastapi/dependencies",
        files: ["dependencies", "params.py"],
        tech: "Python",
      },
      {
        name: "Middleware",
        path: "fastapi/middleware",
        files: ["middleware.py"],
        tech: "Python · FastAPI",
      },
      {
        name: "Compatibility",
        path: "fastapi/compat",
        files: ["compat.py"],
        tech: "Python",
      },
      {
        name: "OpenAPI",
        path: "fastapi/openapi",
        files: ["utils.py", "models.py"],
        tech: "Python · OpenAPI",
      },
      {
        name: "Security",
        path: "fastapi/security",
        files: ["security.py"],
        tech: "Python · JWT",
      },
    ],
  },

  devora: {
    url: "https://github.com/acme/devora",

    modules: [
      {
        name: "Cockpit UI",
        path: "frontend/components",
        files: ["cockpit.tsx", "devora-context.tsx"],
        tech: "Next.js · React",
      },
      {
        name: "Bob Assistant",
        path: "backend/bob",
        files: ["BobController.ts", "ContextRetriever.ts"],
        tech: "TypeScript · LLM",
      },
      {
        name: "Knowledge Engine",
        path: "backend/knowledge-engine",
        files: ["Ingestion.ts", "Embeddings.ts"],
        tech: "Python · Vector DB",
      },
      {
        name: "Session Guard",
        path: "frontend/components",
        files: ["guard.tsx", "session-provider.tsx"],
        tech: "React · JWT",
      },
    ],
  },

  "orders-service": {
    url: "https://github.com/acme/orders-service",

    modules: [
      {
        name: "Order Intake",
        path: "backend/orders",
        files: ["OrderController.ts", "OrderValidator.ts"],
        tech: "TypeScript · SQL",
      },
      {
        name: "Inventory",
        path: "backend/inventory",
        files: ["InventoryService.ts", "StockReserver.ts"],
        tech: "TypeScript · Redis",
      },
      {
        name: "Fulfillment",
        path: "backend/fulfillment",
        files: ["FulfillmentWorker.ts", "ShippingClient.ts"],
        tech: "Worker · Kafka",
      },
      {
        name: "Returns",
        path: "backend/returns",
        files: ["ReturnService.ts"],
        tech: "TypeScript",
      },
    ],
  },
};


// ============================================================
// BROADCASTS
// ============================================================

export const broadcasts = [
  {
    id: "n1",
    audience: "All",
    time: "09:42",
    title: "Sprint checkpoint",
    body: "Local Setup and API Integration are the team focus today. Use Bob for documentation-grounded questions.",
  },
  {
    id: "n2",
    audience: "Frontend Developers",
    time: "Yesterday",
    title: "UI contract freeze",
    body: "Keep API client changes isolated to the frontend adapter until the backend merge.",
  },
  {
    id: "n3",
    audience: "Backend Developers",
    time: "Yesterday",
    title: "Parser handoff",
    body: "Repository parser output should remain structured JSON and flow through the central controller.",
  },
];


// ============================================================
// KNOWLEDGE GAPS
// ============================================================

export const knowledgeGaps = [
  {
    question: "How does reconciliation retry work?",
    count: 5,
    status: "Open",
  },
  {
    question: "Where is Kafka configured?",
    count: 3,
    status: "Open",
  },
  {
    question: "Which service owns refund state?",
    count: 2,
    status: "Review",
  },
  {
    question: "What is the production ingestion schedule?",
    count: 2,
    status: "Open",
  },
];