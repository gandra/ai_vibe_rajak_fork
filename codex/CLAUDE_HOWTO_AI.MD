# Claude code

## Running Claude Code in Container After Setup


```
# Start the container in background (detached mode)
docker start claude-container_course_ai_vibe_rajak_fork
docker stop claude-container_course_ai_vibe_rajak_fork
docker rm claude-container_course_ai_vibe_rajak_fork

# Then access the container's console
docker exec -it claude-container_course_ai_vibe_rajak_fork bash

# Run Claude Code
claude
```


## Setup in container

### 1. Folder.devcontainer
Download the .devcontainer folder from https://github.com/anthropics/claude-code and place it in the project root and then execute:
```
chmod +x .devcontainer/init-firewall.sh
```

### 2. Dockerfile

Open .devcontainer/Dockerfile and change the line:  
```
COPY init-firewall.sh /usr/local/bin/
```
to
```
COPY .devcontainer/init-firewall.sh /usr/local/bin/
```


Build docker file:
```
docker build -f .devcontainer/Dockerfile -t claude-sandbox .
```

### 3. Install and Run Claude Code in Container

Run the following command in terminal to start the container:   
```
docker run -it --name claude-container_course_ai_vibe_rajak_fork \
  --cap-add=NET_ADMIN \
  --cap-add=NET_RAW \
  -v "$(pwd):/workspace" \
  -v claude-code-bashhistory:/commandhistory \
  claude-sandbox
```

While the container is running, open a new terminal and execute:  
```
docker exec -it claude-container_course_ai_vibe_rajak_fork bash
```

Instalirajte Claude Code unutar kontejnera:  
```
npm install -g @anthropic-ai/claude-code
```

Install Claude Code inside the container:  
```
claude auth
claude --dangerously-skip-permissions
```

