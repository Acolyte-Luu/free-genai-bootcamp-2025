# Frontend API Integration Documentation

This document outlines the steps taken to connect the `lang-portal-react` frontend application to the Go backend API (`lang-portal/backend-go`), based largely on the specifications found in `lang-portal/Backend-Technical-Specs.md`.

## Goal

Replace mock data and placeholder functionality in the React frontend with live data fetched from the Go backend API endpoints.

## General Approach

1.  **API Client:** Leveraged the existing `@tanstack/react-query` setup for fetching, caching, and managing server state (loading, errors).
2.  **TypeScript Types:** Defined TypeScript interfaces (`src/types/api.ts`) corresponding to the expected JSON structures of API responses based on the backend specs. These were adjusted as needed based on actual API behavior discovered during integration.
3.  **API Utility Functions:** Created helper functions (`src/lib/api.ts`) to encapsulate `fetch` calls to specific backend endpoints, handling base URL construction and basic response/error handling. The base URL defaults to `http://localhost:8080/api` but can be configured via the `VITE_API_URL` environment variable.
4.  **Component Refactoring:** Replaced mock data arrays and placeholder logic within page components (`src/pages/*`) with `useQuery` hooks calling the relevant API utility functions. Updated component rendering logic to use fetched data, handle loading/error states, and adapt to API data structures.

## Component-Specific Integration

| Component             | File Path                              | Backend Endpoint(s) Connected                                    | Notes                                                                                                     |
| :-------------------- | :------------------------------------- | :--------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------- |
| Words List          | `src/pages/Words.tsx`                  | `GET /api/words`                                                 | Fetches & displays paginated word list. Handles client-side sorting. Audio playback disabled (no URL in API). |
| Word Detail         | `src/pages/WordShow.tsx`               | `GET /api/words/:id`                                             | Fetches & displays details for a single word, including associated groups. Handles missing `audioUrl`/`examples`. |
| Groups List         | `src/pages/Groups.tsx`                 | `GET /api/groups`                                                | Fetches & displays paginated group list. Word count column removed (not in API response).                   |
| Group Detail        | `src/pages/GroupShow.tsx`              | `GET /api/groups/:id`<br>`GET /api/groups/:id/words`<br>`GET /api/groups/:id/study_sessions` | Fetches group details, words list, and session history. Handles nested responses, missing stats.          |
| Dashboard           | `src/pages/Dashboard.tsx`              | `GET /api/dashboard/last_study_session`<br>`GET /api/dashboard/study_progress` | Fetches & displays recent activity and progress cards.                                                    |
| Settings            | `src/pages/Settings.tsx`               | (None)                                                           | Dark Mode implemented client-side (`localStorage`, CSS class). Reset History requires backend endpoints.    |
| Vocabulary Importer | `src/components/VocabularyImporter.tsx` | `POST /generate-vocabulary` (Undocumented)                       | Calls backend to generate vocab based on theme. Displays response. Saving generated words not implemented.  |
| Study Activities    | `src/pages/StudyActivities.tsx`      | (None)                                                           | Kept using mock data for activity list. Launch buttons configured.                                        |
| Sessions List       | `src/pages/Sessions.tsx`               | (N/A)                                                            | Component deleted. Functionality moved to `GroupShow.tsx`.                                                  |

## Helper Files Created

*   **`src/types/api.ts`:** Contains TypeScript interfaces for API request/response structures.
*   **`src/lib/api.ts`:** Contains async functions for fetching data from specific API endpoints.
*   **`src/contexts/ThemeContext.tsx`:** Manages client-side dark/light theme state and applies CSS classes.

## Key Issues & Resolutions During Integration

*   **Nested API Responses:** The actual response for `GET /api/groups/:id/words` had the `data` array and `pagination` object nested within a top-level `data` object (`{data: {data: [], pagination: {}}}`), differing from the spec examples for other endpoints. The frontend types (`GroupWordsApiResponse`) and data access logic (`GroupShow.tsx`) were adjusted accordingly. *Assumption:* The `GET /api/groups/:id/study_sessions` response is assumed *not* nested for now, but this may need adjustment.
*   **Missing `stats` Object (GroupShow):** Encountered errors reading `total_word_count` because `group.stats` was sometimes undefined in the `/api/groups/:id` response. Resolved using optional chaining (`group.stats?.total_word_count`) in `GroupShow.tsx`.
*   **Missing `stats` Object (Words in GroupShow):** Encountered errors reading `correct_count` on words within the `/api/groups/:id/words` response. Resolved using optional chaining in both sorting logic (`a.stats?.[field]`) and rendering (`word.stats?.correct_count`) in `GroupShow.tsx`.
*   **Dark Mode Styling:** Dark mode toggle initially only changed the class; it didn't apply styles because the dark theme CSS variables were missing. Added `.dark { ... }` definitions to `src/index.css`.

## Pending Items & Backend Dependencies

*   **Reset History Endpoint:** Settings page requires a backend endpoint (e.g., `DELETE /api/user/history`) to implement the reset functionality.
*   **Save Vocabulary Endpoint(s):** Vocabulary Importer needs backend endpoint(s) (e.g., `POST /api/words/batch`) to save the generated vocabulary to the database, unless `POST /generate-vocabulary` already handles this (behavior currently unknown).
*   **Get Study Activities Endpoint:** To replace mock data in `StudyActivities.tsx`, a backend endpoint (e.g., `GET /api/study_activities`) is needed.
*   **Sessions API Response Structure:** Verify the actual JSON structure for `GET /api/groups/:id/study_sessions` (nested vs. flat) and adjust `GroupSessionsApiResponse` and `GroupShow.tsx` if necessary.
*   **`POST /generate-vocabulary` Behavior:** Need documentation/clarification on the exact request/response structure and side effects (does it save?) of this undocumented endpoint used by the Vocabulary Importer.
*   **Environment Variable:** The frontend relies on `VITE_API_URL` being set in the environment (e.g., `.env`) to point to the correct backend URL.
*   **CORS:** The Go backend must be configured to accept requests from the frontend's origin (e.g., `http://localhost:8081` during development).

# External Application Integration (`jp-mud`)

Separate from the Go backend integration, configuration was done to link specific UI elements to the external `jp-mud` application running at `http://localhost:5173/`.

## Affected Components:

*   `src/pages/StudyActivities.tsx`: The page displaying the list of available study activities.
*   `src/pages/StudyActivityShow.tsx`: The page displaying details for a single study activity.

## Changes Made:

1.  **Identified Target Buttons:** Located the "Launch" button on the `StudyActivities` page card for "Adventure MUD" and the "Launch Activity" button on the `StudyActivityShow` page when viewing the "Adventure MUD" activity.
2.  **Modified `handleLaunch` Functions:** The `handleLaunch` function within both components was modified.
3.  **Conditional Navigation:** Logic was added to check the `activityId` (in `StudyActivities.tsx`) or the loaded `activity.id` (in `StudyActivityShow.tsx`).
4.  **Action:** If the ID matches the one assumed for "Adventure MUD" (ID `1` based on mock data), the code now sets `window.location.href` to `'http://localhost:5173/'`, navigating the current browser tab to the `jp-mud` application.
5.  **Default Behavior:** For any other activity ID, the original behavior (opening `http://localhost:8080?group_id=...` in a new tab using `window.open()`) was retained. 