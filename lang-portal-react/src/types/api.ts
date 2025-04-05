export interface ApiWord {
  id: number;
  japanese: string;
  romaji: string;
  english: string;
  parts: string;
  correct_count: number;
  incorrect_count: number;
  created_at: string; // Assuming ISO 8601 date string
}

export interface Pagination {
  current_page: number;
  total_pages: number;
  total_items: number;
  items_per_page: number;
}

export interface WordApiResponse {
  data: ApiWord[];
  pagination: Pagination;
}

// Type for associated groups in single word response
export interface ApiGroupInfo {
  id: number;
  name: string;
}

// Type for the /api/words/:id response
export interface SingleWordApiResponse {
  data: ApiWord;       // The word itself
  groups: ApiGroupInfo[]; // Associated groups
}

// Type for a group object from /api/groups endpoint
export interface ApiGroup {
  id: number;
  name: string;
  created_at: string; // Assuming ISO 8601 date string
  // Note: wordCount is not directly available in this endpoint per spec
  // It might be available in /api/groups/:id or calculated differently
}

// Type for the /api/groups response
export interface GroupApiResponse {
  data: ApiGroup[];
  pagination: Pagination;
}

// --- Types for /api/groups/:id ---
export interface GroupStats {
  total_word_count: number;
}

export interface SingleGroupData extends ApiGroup { // Reuse ApiGroup for base fields
  stats: GroupStats;
  // Add description if it becomes available in the API
}

export interface SingleGroupApiResponse {
  data: SingleGroupData;
}

// --- Types for /api/groups/:id/words ---
export interface GroupWordStats {
  correct_count: number;
  incorrect_count: number;
}

export interface GroupWord {
  // Note: Missing 'id' in the provided spec example for this endpoint.
  // Assuming 'japanese' or combination is unique key for rendering list.
  // Or perhaps word ID is needed and missing from spec?
  // id?: number; // Optional for now
  japanese: string;
  romaji: string;
  english: string;
  stats: GroupWordStats;
  // Add parts or other fields from ApiWord if needed/available here
}

export interface GroupWordsApiResponse {
  data: {
    data: GroupWord[];      // Nested word array
    pagination: Pagination; // Nested pagination
  };
  success?: boolean; // Include success flag if needed
}

// --- Types for Dashboard Endpoints ---

// /api/dashboard/last_study_session
export interface LastStudySession {
  id: number;
  group_id: number;
  group_name: string;
  study_activity_id: number;
  created_at: string;
  correct_count: number;
  total_words: number;
}
export interface LastStudySessionApiResponse {
  data: LastStudySession | null; // Data can be null if no sessions yet
}

// /api/dashboard/study_progress
export interface StudyProgress {
  total_words: number;
  total_words_studied: number;
}
export interface StudyProgressApiResponse {
  data: StudyProgress | null; // Allow null if no data
}

// /api/dashboard/quick_stats
export interface QuickStats {
  total_study_sessions: number;
  active_groups: number;
  study_streak: number;
  success_percentage: number;
}
export interface QuickStatsApiResponse {
  data: QuickStats | null; // Allow null if no data
}

// --- Types for /api/groups/:id/study_sessions ---
export interface GroupSession {
  id: number;
  activity_name: string; // Name of the activity (e.g., "Flashcards")
  group_name: string; // Should match the group being viewed
  start_time: string; // ISO 8601 format
  end_time: string;   // ISO 8601 format
  review_items_count: number; // How many words were reviewed
}

export interface GroupSessionsApiResponse {
  data: GroupSession[];
  pagination: Pagination;
  // Note: Backend spec example showed data wrapped in another data obj like group words
  // Assuming here it's flat for now based on spec text, adjust if needed.
  /* Alternative if nested:
  data: {
    data: GroupSession[];
    pagination: Pagination;
  }
  */
}

// Add other API response types here as needed 