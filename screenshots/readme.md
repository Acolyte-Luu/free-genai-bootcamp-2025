## Getting the JP MUD application to run.

Hi Andrew, so i think the issue you had when trying to run my app i think is you might now have the latest version of my repo. i went through your feedback video again and it looks like you are missing a file in the jp-md/frontend/src/components/ui path. Thereare supposed to be three files there. Button.tsx, button.tsx and input.tsx, but for some reason in the video there are only two files, button.tsx and input.tsx. The other issue is my fault because thelib/utils path was ignored by my gitignore file thats why you ran into that issue. I will fix this when i upload the screenshots. I think for the backend immade so many adjutments in my virtual environment to get things working so that may be why there were some version mismatches and compatibility issues in there. I added a screen capture vidoe of the application running, I hope this helps.


### In the case of serving ollama locally, this was achieved using docker. So to get this running you have to first cd into my opea-comps directory. there is a dcoker compose file there. there is also a readme file there which details how to get the ollama server running with your GPU. I will just add those steps here in case. 

### In the case of getting my main application backend to run you cd to my lang-portal directory and run this command .... go run cmd/server/main.go ....

## To get the main frontend app running.

**Navigate to Frontend Directory:**
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



#### I really hope you get the time and chance to run pass over this again.

# Novelty
I got my LLM to run using my dedicated NVIDIA GPU.
This was achieved by installing the nvidia container toolkit package. I also had to turn on the integration for my GPU in docker desktop since I am running on WSL2. Modified the docker compose file to use the nvidia image.

## Steps

1. Install the nvidia container toolkit
```sh
# Remove any existing NVIDIA Docker sources
sudo rm /etc/apt/sources.list.d/nvidia-container-runtime.list

# Add NVIDIA repository and GPG key using the new method
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Update package listing
sudo apt-get update

# Install NVIDIA Container Toolkit
sudo apt-get install -y nvidia-container-toolkit

# Configure the Docker daemon to recognize the NVIDIA Container Runtime
sudo nvidia-ctk runtime configure --runtime=docker

# Restart Docker daemon by relaunching docker desktop
```

If this does not work, you can try the following:
1. First, make sure you have the NVIDIA CUDA driver installed on Windows (host system)

2.Edit or create a .wslconfig file in your Windows user directory (C:\Users\YourUsername\.wslconfig):
```sh
[wsl2]
gpuSupport=true
```

3. Update your WSL kernel to support NVIDIA GPUs. From PowerShell (as Administrator):
```sh
wsl --update
```

4. Make sure you have the CUDA toolkit installed in your WSL environment:
```sh
sudo apt-get update
sudo apt-get install -y nvidia-cuda-toolkit
```

5. Turn on the integration for my GPU in docker desktop

6. Modify the docker compose file to use the nvidia image
  docker compose file in this repo

7. Run the docker compose file
```sh
HOST_IP=$(hostname -I | awk '{print $1}') NO_PROXY=localhost LLM_ENDPOINT_PORT=9000 LLM_MODEL_ID="llama3.1:8b" docker compose up
```

Once the Ollama server is running we can make API calls to the ollama API

https://github.com/ollama/ollama/blob/main/docs/api.md


## Download (Pull) a model

curl http://localhost:9000/api/pull -d '{
  "model": "llama3.1:8b"
}'
so i use this curl command to download ech of the models that i used. you just have to replace the model aprameter with the specific model you want to pull.



