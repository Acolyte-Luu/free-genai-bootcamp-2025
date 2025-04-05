# Lang Portal React Frontend

This directory contains the React frontend application for the Language Learning Portal, built with Vite, TypeScript, Tailwind CSS, and shadcn/ui.

## Prerequisites

*   **Node.js:** (Recommend LTS version) - Download from [nodejs.org](https://nodejs.org/)
*   **npm:** (Node Package Manager) - Comes bundled with Node.js.
*   *Optional:* `bun` or `yarn` can also be used, but this guide prioritizes `npm`.

## Setup & Installation

1.  **Clone the Repository:** If you haven't already, clone the main project repository.

2.  **Navigate to Frontend Directory:**
    ```bash
    cd path/to/free-genai-bootcamp-2025/lang-portal-react
    ```

3.  **Install Dependencies:**
    Using npm:
    ```bash
    npm install
    ```

## Configuration

The application needs to know the URL of the backend API.

1.  **Create `.env` file:** Create a file named `.env` in the `lang-portal-react` directory.

2.  **Set API URL:** Add the following line to the `.env` file, replacing the URL with the actual address where your Go backend is running:
    ```env
    VITE_API_URL=http://localhost:8080/api 
    ```
    (The default port for the Go backend is often 8080, adjust if necessary).

## Required Running Services

Before running the React development server, ensure the following backend services are running:

1.  **Go Backend API (`lang-portal/backend-go`):**
    *   Provides the main data API for words, groups, sessions, and dashboard stats.
    *   Make sure this backend is running and accessible at the URL specified in your `.env` file (e.g., `http://localhost:8080`). Refer to the Go backend's documentation for instructions on how to run it.

2.  **`jp-mud` Application (Optional, for Adventure MUD):**
    *   Required for the "Adventure MUD" study activity link.
    *   If you intend to use this activity, ensure the `jp-mud` frontend is running, typically at `http://localhost:5173/`. Refer to the `jp-mud` project documentation for instructions.

## Running the Development Server

Once dependencies are installed, the `.env` file is configured, and the required backend services are running:

Using npm:
```bash
npm run dev
```