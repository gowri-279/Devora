const DEVORA_API_URL =
  import.meta.env.VITE_DEVORA_API_URL ?? "http://127.0.0.1:8000/api";

export type AssessmentQuestion = {
  question_id: string;
  domain: string;
  question: string;
};

export type Assessment = {
  assessment_id: string;
  status: string;
  project_id: string;
  questions: AssessmentQuestion[];
};

export type AssessmentAnswer = {
  question_id: string;
  answer: string;
};

export type AssessmentResult = {
  assessment_id: string;
  status: string;
  overall_score: number;
  scores: Record<string, number>;
  next_focus: string | null;
  summary: string;
  evidence: Array<Record<string, unknown>>;
  analyzed_by: string;
};

export type LearningPathCourseContent = {
  source_file: string;
  filename: string;
  scope: string;
  content: string;
};

export type LearningPathModule = {
  step: number;
  title: string;
  description: string;
  purpose: string;
  sources: string[];
  course_content: LearningPathCourseContent[];
};

export type LearningPathResponse = {
  project_id: string;
  learning_path: LearningPathModule[];
  repository_summary?: Record<string, unknown>;
  mode: string;
};

export type ModuleProgressResponse = {
  developer_id: string;
  project_id: string;
  completed_modules: Array<{
    module_step: number;
    module_title?: string;
    status: string;
    completed_at?: string;
    updated_at?: string;
  }>;
};

export async function getModuleProgress(
  developerId: string,
  projectId: string,
) {
  const backendUrl = DEVORA_API_URL.replace(/\/api\/?$/, "");

  const response = await fetch(
    `${backendUrl}/modules/progress?developer_id=${encodeURIComponent(
      developerId,
    )}&project_id=${encodeURIComponent(projectId)}`,
  );

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(
      detail || `Devora API request failed (${response.status})`,
    );
  }

  return response.json() as Promise<ModuleProgressResponse>;
}

export function completeModuleProgress(
  developerId: string,
  projectId: string,
  moduleStep: number,
) {
  const backendUrl = DEVORA_API_URL.replace(/\/api\/?$/, "");

  return fetch(
    `${backendUrl}/modules/progress/complete?developer_id=${encodeURIComponent(
      developerId,
    )}&project_id=${encodeURIComponent(
      projectId,
    )}&module_step=${moduleStep}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    },
  ).then(async (response) => {
    if (!response.ok) {
      const detail = await response.text();
      throw new Error(
        detail || `Devora API request failed (${response.status})`,
      );
    }

    return response.json();
  });
}

export function checkModuleQuiz(
  developerId: string,
  projectId: string,
  moduleStep: number,
  answers: number[],
) {
  return request<{
    project_id: string;
    developer_id: string;
    module_step: number;
    module_title: string;
    score: number;
    total: number;
    passed: boolean;
    message?: string;
    unlocked_next_step?: number | null;
  }>("/modules/quiz/check", {
    method: "POST",
    body: JSON.stringify({
      project_id: projectId,
      module_step: moduleStep,
      developer_id: developerId,
      answers,
    }),
  });
}

export function generateModuleQuiz(
  projectId: string,
  moduleStep: number,
) {
  const backendUrl = DEVORA_API_URL.replace(/\/api\/?$/, "");

  return fetch(
    `${backendUrl}/modules/quiz/generate`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        project_id: projectId,
        module_step: moduleStep,
      }),
    },
  ).then(async (response) => {
    if (!response.ok) {
      const detail = await response.text();
      throw new Error(
        detail ||
          `Devora API request failed (${response.status})`,
      );
    }

    return response.json() as Promise<{
      status: string;
      project_id: string;
      module_step: number;
      module_title: string;
      questions: Array<{
        question_id: string;
        question: string;
        options: string[];
      }>;
    }>;
  });
}

export type DeveloperTwin = {
  developer_id: string;
  project_id: string;
  skills: Record<string, number>;
  source: string;
  version: number;
  created_at?: string;
  updated_at?: string;
};

export type DeveloperTwinResponse = {
  status: string;
  developer_twin: DeveloperTwin | null;
};

export async function createDeveloperTwinFromResume(
  developerId: string,
  projectId: string,
  file: File,
) {
  const formData = new FormData();
  formData.append("developer_id", developerId);
  formData.append("project_id", projectId);
  formData.append("file", file);

  const response = await fetch(
    `${DEVORA_API_URL}/developer-twin/from-resume`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(
      detail || `Developer profile upload failed (${response.status})`,
    );
  }

  return response.json() as Promise<DeveloperTwinResponse>;
}

export function createDeveloperTwin(
  developerId: string,
  projectId: string,
  skills: Record<string, number>,
) {
  return request<DeveloperTwinResponse>("/developer-twin", {
    method: "POST",
    body: JSON.stringify({
      developer_id: developerId,
      project_id: projectId,
      skills,
    }),
  });
}

export function getDeveloperTwin(
  developerId: string,
  projectId: string,
) {
  return request<DeveloperTwinResponse>(
    `/developer-twin/${developerId}?project_id=${encodeURIComponent(projectId)}`,
    {
      method: "GET",
    },
  );
}

export function getKnowledgeGaps(
  projectId: string,
  minOccurrences = 1,
  status = "open",
) {
  return request<{
    gaps: Array<{
      gap_id: string;
      query: string;
      example_queries: string[];
      project_id: string;
      top_score: number;
      asked_by_developer_id?: string | null;
      developer_ids?: string[];
      status: string;
      occurrence_count: number;
      first_seen_at: string;
      last_seen_at: string;
      resolved_at?: string;
    }>;
  }>(
    `/gaps?project_id=${encodeURIComponent(projectId)}&min_occurrences=${minOccurrences}&status=${encodeURIComponent(status)}`,
    {
      method: "GET",
    },
  );
}

export function getNotifications(
  recipientId: string,
  role: "developer" | "admin",
) {
  return request<{
    notifications: Array<{
      notification_id?: string;
      recipient_id: string;
      role: string;
      text: string;
      question?: string | null;
      gap_id?: string | null;
      read: boolean;
      created_at: string;
    }>;
  }>(
    `/notifications?recipient_id=${encodeURIComponent(recipientId)}&role=${encodeURIComponent(role)}`,
    {
      method: "GET",
    },
  );
}

export function createNotification(notification: {
  recipientId: string;
  role: "developer" | "admin";
  text: string;
  question?: string;
  gapId?: string;
}) {
  return request<{
    status: string;
    notification_id: string;
  }>("/notifications", {
    method: "POST",
    body: JSON.stringify({
      recipient_id: notification.recipientId,
      role: notification.role,
      text: notification.text,
      question: notification.question ?? null,
      gap_id: notification.gapId ?? null,
    }),
  });
}

export function resolveKnowledgeGap(gapId: string) {
  return request<{
    gap_id: string;
    resolved: boolean;
  }>(
    `/gaps/${encodeURIComponent(gapId)}/resolve`,
    {
      method: "POST",
    },
  );
}

export type RepositoryUploadResponse = {
  message: string;
  repo_url: string;
  project_id: string;
  parser_status: string;
  repository_metadata: Record<string, unknown>;
  ingestion: Record<string, unknown>;
  learning_path: LearningPathResponse;
};

export type DocumentUploadResponse = Record<string, unknown>;
export type ProjectDocument = {
  source_file: string;
  scope: string;
  project_id?: string | null;
  text: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
};

export type DocumentsResponse = {
  project_id: string;
  documents: ProjectDocument[];
};

export function getProjectRepository(projectId: string) {
  return request<{
    project_id: string;
    repo_url: string | null;
    repository: string | null;
  }>(
    `/projects/${encodeURIComponent(projectId)}/repository`,
  );
}

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${DEVORA_API_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(
      detail || `Devora API request failed (${response.status})`,
    );
  }

  return response.json() as Promise<T>;
}

async function uploadFile<T>(
  path: string,
  file: File,
): Promise<T> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `${DEVORA_API_URL}${path}`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(
      detail || `Devora upload failed (${response.status})`,
    );
  }

  return response.json() as Promise<T>;
}

export function createAssessment(
  developerId: string,
  projectId: string,
) {
  return request<Assessment>("/assessments", {
    method: "POST",
    body: JSON.stringify({
      developer_id: developerId,
      project_id: projectId,
    }),
  });
}

export function submitAssessment(
  assessmentId: string,
  developerId: string,
  answers: AssessmentAnswer[],
) {
  return request<AssessmentResult>(
    `/assessments/${assessmentId}/submit`,
    {
      method: "POST",
      body: JSON.stringify({
        developer_id: developerId,
        answers,
      }),
    },
  );
}

export function getLearningPath(
  developerId: string,
  projectId: string,
) {
  return request<LearningPathResponse>("/learning-path", {
    method: "POST",
    body: JSON.stringify({
      developer_id: developerId,
      project_id: projectId,
    }),
  });
}

export function uploadRepository(
  repoUrl: string,
) {
  return request<RepositoryUploadResponse>(
    "/upload/repository",
    {
      method: "POST",
      body: JSON.stringify({
        repo_url: repoUrl,
      }),
    },
  );
}

export function uploadDocument(
  projectId: string,
  file: File,
) {
  return uploadFile<DocumentUploadResponse>(
    `/upload/documents?project_id=${encodeURIComponent(projectId)}`,
    file,
  );
}

export function getProjectDocuments(
  projectId: string,
  includeArchived = false,
) {
  return request<DocumentsResponse>(
    `/documents?project_id=${encodeURIComponent(
      projectId,
    )}&include_archived=${includeArchived}`,
  );
}

