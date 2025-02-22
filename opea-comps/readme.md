## Running Ollama Third-Party Service

### Choosing a Model

You can get the model_id that ollama will launch from the [Ollama Library](https://ollama.com/library).

https://ollama.com/library/llama3.2

eg. LLM_MODEL_ID="llama3.2:1b"

### Getting the Host IP

#### Linux

Get your IP address
```sh
sudo apt install net-tools
ifconfig
```

Or you can try this way `$(hostname -I | awk '{print $1}')`

HOST_IP=$(hostname -I | awk '{print $1}') NO_PROXY=localhost LLM_ENDPOINT_PORT=9000 LLM_MODEL_ID="llama3.2:1b" docker compose up


### Ollama API

Once the Ollama server is running we can make API calls to the ollama API

https://github.com/ollama/ollama/blob/main/docs/api.md


## Download (Pull) a model

curl http://localhost:9000/api/pull -d '{
  "model": "llama3.2:1b"
}'

## Generate a Request

curl http://localhost:9000/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "Why is the sky blue?"
}'

# Technical Uncertainty

Q Does bridge mode mean we can only accses Ollama API with another model in the docker compose?

A No, the host machine will be able to access it

Q: Which port is being mapped 8008->141414

In this case 8008 is the port that host machine will access. the other other in the guest port (the port of the service inside container)

Q: If we pass the LLM_MODEL_Id to the ollama server will it download the model when on start?

It does not appear so. The ollama CLI might be running multiple APIs so you need to call the /pull api before trying to generate text

Q: Will the model be downloaded in the container? does that mean the ml model will be deleted when the container stops running?

A: The model will download into the container, and vanish when the container stop running. You need to mount a local drive and there is probably more work to be done.

Q: For LLM service which can text-generate it suggets it will only work with TGI/vLLM and all you have to do is have it running. Does TGI and vLLM have a stardarized API or is there code to detect which one is running? Do we have to really use Xeon or Guadi processor?

vLLM, TGI (Text Generation Inference), and Ollama all offer APIs with OpenAI compatibility, so in theory they should be interchangable.

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
HOST_IP=$(hostname -I | awk '{print $1}') NO_PROXY=localhost LLM_ENDPOINT_PORT=9000 LLM_MODEL_ID="llama3.2:1b" docker compose up
```
