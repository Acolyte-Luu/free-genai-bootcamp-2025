import { WordApiResponse, SingleWordApiResponse, GroupApiResponse, SingleGroupApiResponse, GroupWordsApiResponse } from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api'; // Default to localhost:8080/api

export const fetchWords = async (page = 1, limit = 50): Promise<WordApiResponse> => {
  const response = await fetch(`${API_BASE_URL}/words?page=${page}&limit=${limit}`);
  
  if (!response.ok) {
    // Consider more specific error handling based on response status
    throw new Error('Network response was not ok'); 
  }

  const data = await response.json();
  return data as WordApiResponse; // Add type assertion
};

// Add function to fetch a single word
export const fetchWordById = async (id: string | number): Promise<SingleWordApiResponse> => {
  const response = await fetch(`${API_BASE_URL}/words/${id}`);
  
  if (!response.ok) {
    // Handle specific errors like 404 Not Found if needed
    throw new Error('Network response was not ok'); 
  }

  const data = await response.json();
  return data as SingleWordApiResponse; 
};

// Add function to fetch groups
export const fetchGroups = async (page = 1, limit = 50): Promise<GroupApiResponse> => {
  // TODO: Add sorting parameters if backend supports them
  const response = await fetch(`${API_BASE_URL}/groups?page=${page}&limit=${limit}`);
  
  if (!response.ok) {
    throw new Error('Network response was not ok'); 
  }

  const data = await response.json();
  return data as GroupApiResponse; 
};

// Add function to fetch single group details
export const fetchGroupById = async (id: string | number): Promise<SingleGroupApiResponse> => {
  const response = await fetch(`${API_BASE_URL}/groups/${id}`);
  
  if (!response.ok) {
    // Handle 404 etc.
    throw new Error('Network response was not ok'); 
  }
  const data = await response.json();
  return data as SingleGroupApiResponse; 
};

// Add function to fetch words for a specific group
export const fetchWordsForGroup = async (groupId: string | number, page = 1, limit = 50): Promise<GroupWordsApiResponse> => {
  const response = await fetch(`${API_BASE_URL}/groups/${groupId}/words?page=${page}&limit=${limit}`);
  
  if (!response.ok) {
    throw new Error('Network response was not ok'); 
  }
  const data = await response.json();
  return data as GroupWordsApiResponse; 
};

// --- Dashboard API Functions ---
import { 
  LastStudySessionApiResponse, 
  StudyProgressApiResponse, 
  QuickStatsApiResponse 
} from '@/types/api';

export const fetchLastStudySession = async (): Promise<LastStudySessionApiResponse> => {
  const response = await fetch(`${API_BASE_URL}/dashboard/last_study_session`);
  if (!response.ok) {
    // Allow for 404 or other non-error states where data might be null
    if (response.status === 404) return { data: null }; 
    throw new Error('Network response was not ok'); 
  }
  const data = await response.json();
  return data as LastStudySessionApiResponse; 
};

export const fetchStudyProgress = async (): Promise<StudyProgressApiResponse> => {
  const response = await fetch(`${API_BASE_URL}/dashboard/study_progress`);
  if (!response.ok) {
    if (response.status === 404) return { data: null }; 
    throw new Error('Network response was not ok'); 
  }
  const data = await response.json();
  return data as StudyProgressApiResponse; 
};

export const fetchQuickStats = async (): Promise<QuickStatsApiResponse> => {
  const response = await fetch(`${API_BASE_URL}/dashboard/quick_stats`);
  if (!response.ok) {
    if (response.status === 404) return { data: null }; 
    throw new Error('Network response was not ok'); 
  }
  const data = await response.json();
  return data as QuickStatsApiResponse; 
};

// Add function to fetch sessions for a specific group
import { GroupSessionsApiResponse } from '@/types/api';

export const fetchSessionsForGroup = async (groupId: string | number, page = 1, limit = 10): Promise<GroupSessionsApiResponse> => {
  // Using lower limit for sessions by default
  const response = await fetch(`${API_BASE_URL}/groups/${groupId}/study_sessions?page=${page}&limit=${limit}`);
  
  if (!response.ok) {
    if (response.status === 404) return { data: [], pagination: { current_page: 1, total_pages: 0, total_items: 0, items_per_page: limit } }; // Return empty if no sessions
    throw new Error('Network response was not ok'); 
  }
  const data = await response.json();
  // TODO: Check if data needs nested access (data.data / data.pagination) based on actual API response
  return data as GroupSessionsApiResponse; 
};

// Add other API fetching functions here... 