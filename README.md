# AI SMM Platform for B2B

## Overview

The AI SMM Platform is a comprehensive B2B marketing campaign generator built to help businesses create, translate, and evaluate professional social media content for Instagram, Facebook, Telegram, and LinkedIn. Leveraging OpenAI's GPT models, this platform generates platform-optimized marketing content, translates it into 15+ languages, and evaluates quality using the G-Eval framework. It's designed with an intuitive interface using Streamlit to facilitate interaction and customization.

## Target Audience

### 🎯 Who Is This For?

This platform is designed for B2B businesses that need professional, scalable content creation for social media marketing.

#### Primary Persona: Small Business Owners (60% of users)

**Example: Alex Rodriguez, 35** - Owner of FitZone Fitness (3 locations, 15 employees, $500k/year revenue)

**Pain Points:**
- No time for social media (12-hour workdays)
- Can't afford marketing agency ($2k-5k/month)
- Canva takes too long (3 hours per post)
- No idea what content works
- Needs multilingual content (English + Spanish for Hispanic clients)
- Needs content for Instagram, Facebook, Telegram

**Current Workflow:** 2.5 hours per post × 5 posts/week = **12.5 hours/week**

**What Alex Needs:**
- ✅ Create post in 15 min (not 2.5 hours)
- ✅ Templates for recurring content types
- ✅ Know WHAT works and WHY
- ✅ Auto-translate to multiple languages
- ✅ Platform-specific optimization

**Willingness to Pay:** $49-199/month

#### Secondary Persona: Marketing Managers (30% of users)

**Example: Jessica Kim, 29** - Marketing Manager at CloudFlow SaaS ($2M ARR, 50 employees)

**Pain Points:**
- Small team (just her + intern)
- Needs 20+ posts/week
- B2B content must be professional
- Currently: Jasper ($99) + Canva ($13) = $112/mo + 15h/week
- CEO asks "what's ROI?" - no clear answer

**What Jessica Needs:**
- ✅ One tool (replace Jasper + Canva)
- ✅ B2B-focused (not generic B2C)
- ✅ Custom templates for product releases, case studies, webinars
- ✅ Analytics that prove ROI
- ✅ Multi-language (US + EU markets)

**Willingness to Pay:** $79-300/month

#### Tertiary Persona: Digital Agencies (10% of users)

**Example: Carlos Santos, 38** - Founder of Digital Boost Agency (25 clients, 12 employees)

**Pain Points:**
- Each client needs custom templates
- Hard to scale (hire more = lower margin)
- Clients ask "why no viral?"
- 12 hours/client/month × 25 = **300 hours/month** = need 4 full-time employees

**What Carlos Needs:**
- ✅ White-label solution
- ✅ Custom template per client
- ✅ Bulk generation (20 posts at once)
- ✅ Analytics clients understand
- ✅ Multi-user (his 12 employees)

**Willingness to Pay:** $299-1,500/month

## Industries We Serve

- **Fitness & Wellness**: Gyms, yoga studios, personal trainers, nutrition coaches
- **E-commerce**: Fashion, electronics, handmade goods, dropshipping
- **SaaS & Tech**: Software companies, apps, developer tools, cloud services
- **Consulting**: Business consulting, coaching, training, advisory
- **Local Services**: Dentists, lawyers, accountants, real estate
- **Digital Agencies**: Marketing agencies serving multiple clients
- **Education**: Online courses, tutoring, schools, training programs
- **Food & Beverage**: Restaurants, cafes, catering, food delivery

## Features

1. **Content Generation**: Automatically generate campaign content using templates and user queries.
2. **Translation**: Convert the content into multiple languages while preserving context and style.
3. **Criticism and Reflection**: Improve translations by integrating criticism and suggestions.
4. **Evaluation**: Assess translations using metrics like fluency, accuracy, and cultural appropriateness.
5. **Template Customization**: Use and modify content templates for structured marketing efforts.
6. **Interactive UI**: Built with Streamlit for easy user interaction and content management.
7. **Campaign Management**: Save, retrieve, and manage campaigns for future use.

## Technical Approach

## Agents Overview

### ContentGenerationAgent

- **Purpose**: Generates marketing content based on user input and templates, using additional context to enhance the output.

- **Patterns**:
  - **Retrieval-Augmented Generation (RAG)**: Enhances content by retrieving similar campaigns from a database, adding context to the generation process.

- **Libraries**:
  - **Langchain Core**: Facilitates message formatting and state management.
  - **Langgraph**: Manages the state graph for seamless execution flow.
  - **Milvus**: A vector database used for storing and retrieving campaign embeddings to find similar content for context provisioning.

- **AI Models**: Utilizes OpenAI models (gpt-4o-mini, gpt-4o) for content creation, augmented with retrieved context to improve relevance and coherence.

This approach leverages the strengths of both retrieval and generation methods, ensuring that the content is not only creative but also contextually rich and relevant.

### TranslationAgent

- **Purpose**: Translates generated content into multiple languages, while handling criticism and improvement through reflection.
- **Patterns**: Employs a [Reflection](https://blog.langchain.dev/reflection-agents/) pattern: graph-based state machine (`StateGraph`) with nodes for translation, criticism, and reflection.
- **Libraries**:
  - **Langchain Core**: For message and prompt management.
  - **Langgraph**: Controls the logical flow of translation tasks.

- **AI Models**: Leverages OpenAI models for language translation and refinement operations.

### EvaluationAgent

- **Purpose**: Evaluates translations against selected metrics to ensure quality and cultural relevancy.
- **Patterns**: Implements metric-based evaluation using [G-Eval framework](https://docs.confident-ai.com/docs/metrics-llm-evals).
- **Libraries**:
  - **DeepEval**: Provides tools for creating test cases and applying various evaluation metrics.
- **AI Models**: Utilizes the DeepEval framework with OpenAI models for scoring translations on aspects like fluency and accuracy.

Each agent interacts with OpenAI models to perform specific tasks, using state management and evaluation frameworks to ensure quality and efficiency.

## File Structure
```
root/
├── agents/
│   ├── content_generation_agent.py # ContentGenerationAgent class for content generation
│   ├── translation_agent.py        # TranslationAgent class with reflection pattern
│   ├── evaluation_agent.py         # EvaluationAgent class for translation evaluation
│   └── agent_state.py              # Shared state schema (TypedDict)
├── repositories/
│   ├── campaign_repository.py      # Campaign CRUD + vector search (MongoDB + Milvus)
│   ├── audience_repository.py      # Audience management
├── utils/
│   ├── openai_utils.py             # OpenAI client and embedding generation
│   ├── deepeval_openai.py          # OpenAI wrapper for DeepEval framework
│   ├── mongodb_utils.py            # MongoDB client utilities
│   ├── llm_queries.py              # Default prompts for agents
│   └── ui_components.py            # Streamlit UI components
├── pages/
│   ├── 02_OpenAI_Check.py          # OpenAI API connectivity test
│   └── ... (other pages)
├── seeding_scripts/
│   ├── insert_tempaltes.py         # Load B2B content templates
│   └── insert_audiences.py         # Load B2B audiences
├── static/
│   ├── images/                     # Logos, brand images
│   └── ui/                         # UI assets
├── docs/                           # Documentation files
├── Home.py                         # Main Streamlit application
├── campaign.py                     # Campaign data model
├── audience.py                     # Audience data model
├── pyproject.toml                  # Poetry dependencies
└── README.md                       # Project documentation
```
## How to Run

### Local Development Setup

**Prerequisites:**
- Python 3.11 (required: >=3.11,<3.13)
- Docker (for MongoDB)
- Poetry (for dependency management)

**Installation Steps:**

1. **Install Python 3.11** (macOS):
   ```bash
   brew install python@3.11
   ```

2. **Create Virtual Environment**:
   ```bash
   /usr/local/bin/python3.11 -m venv .venv
   ```

3. **Install Poetry in venv**:
   ```bash
   .venv/bin/pip install poetry
   ```

4. **Install Dependencies**:
   ```bash
   .venv/bin/poetry install --no-root
   ```

5. **Install WeasyPrint System Libraries**:

   **macOS:**
   ```bash
   brew install cairo pango gdk-pixbuf libffi gobject-introspection
   ```

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev libcairo2 libpangoft2-1.0-0
   ```

6. **Setup MongoDB via Docker**:
   ```bash
   docker-compose up -d mongodb
   ```

7. **Create `.env` file** with your OpenAI API key:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_ENDPOINT=https://api.openai.com/v1  # Optional, defaults to official OpenAI

   # Language Configuration
   LANGUAGES=uk-UA,pl-PL,kk-KZ,es-ES,zh-CN,fr-FR,de-DE,hi-IN,ar-SA,pt-BR,ru-RU,ja-JP,ko-KR,it-IT,tr-TR
   DEFAULT_LANGUAGES=uk-UA

   # Database Connections
   CONNECTION_STRING_MONGO=mongodb://admin:password123@localhost:27017/marketing_db?authSource=admin
   CONNECTION_STRING_MILVUS=http://root:Milvus@localhost:19530

   # Monitoring (optional)
   SENTRY_DSN=
   ```

8. **Run Streamlit** (через Poetry):
   ```bash
   poetry run streamlit run Home.py
   ```

   Или с дополнительными параметрами:
   ```bash
   poetry run streamlit run Home.py --server.port=8501 --server.headless=true
   ```

9. **Access Application**:
   Open http://localhost:8501 in your browser

### Quick Start Commands

```bash
# Start MongoDB
docker-compose up -d mongodb

# Run application
poetry run streamlit run Home.py

# Load templates (if needed)
poetry run python seeding_scripts/insert_tempaltes.py
```

### Production Deployment (GCP Server)

**Prerequisites:**
- GCP e2-standard-2 instance (8GB RAM recommended)
- Docker and Docker Compose installed

**Installation Steps:**

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment Variables**: Create a `.env` file with your OpenAI API key:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_ENDPOINT=https://api.openai.com/v1  # Optional

   # Languages
   LANGUAGES=uk-UA,pl-PL,kk-KZ,es-ES,zh-CN,fr-FR,de-DE,hi-IN,ar-SA,pt-BR,ru-RU,ja-JP,ko-KR,it-IT,tr-TR
   DEFAULT_LANGUAGES=uk-UA

   # Database
   CONNECTION_STRING_MONGO=mongodb://admin:password123@localhost:27017/marketing_db?authSource=admin

   # Monitoring (optional)
   SENTRY_DSN=
   ```

### Running the Application

#### Running on localhost

1. **Check Prerequisites**: Ensure all prerequisites are installed.
2. **Create .env File**: Copy and adjust the example `.env` file:
   ```bash
   cp .env.example .env
   ```
3. **Install Dependencies**: 
   ```bash
   poetry install
   ```
4. **Run the Application**: 
   ```bash
   poetry run streamlit run Home.py
   ```

#### Running with `docker-compose`

1. **Configure Local Environment**: Set up the local environment.
2. **Ensure Docker is Available**: 
   ```bash
   docker info
   ```
3. **Run Shared Services**: 
   ```bash
   make services-start
   ```
4. **Build and Run the Application**:
   ```bash
   make app-bootcamp-build NAME=<your-app-folder-name>
   make app-bootcamp-start NAME=<your-app-folder-name>
   ```


---

## 🚀 Deployment on GCP Server

This section describes how to deploy the application on a Google Cloud Platform (GCP) server.

### Server Requirements

**Minimum Configuration:**
- Machine type: **e2-medium** or better
- vCPUs: **2 (dedicated)**
- RAM: **4 GB**
- Disk: **20 GB**
- OS: Ubuntu 22.04 LTS

**Recommended Configuration:**
- Machine type: **e2-standard-2** ⭐
- vCPUs: **2**
- RAM: **8 GB**
- Disk: **30 GB**
- OS: Ubuntu 22.04 LTS

### Current Production Deployment

**Server:** 34.165.120.217 (e2-standard-2)
- Python 3.11.14
- Poetry 2.2.1
- MongoDB in Docker (port 27017)
- Streamlit running directly on server (port 8501)

**Application URL:** http://34.165.120.217:8501

### Deployment Architecture

- **MongoDB**: Running in Docker container using `docker-compose.yml`
- **Streamlit App**: Running directly on server (not in Docker) for easier development and debugging
- **Milvus**: Optional (disabled by default) - only needed for RAG functionality

### Step-by-Step Deployment Guide

#### 1. Create GCP Server

1. Go to **GCP Console** → **Compute Engine** → **VM instances** → **CREATE INSTANCE**
2. Configure:
   - **Machine type**: e2-standard-2 (2 vCPU, 8 GB memory)
   - **Boot disk**: Ubuntu 22.04 LTS, 30 GB
   - **Firewall**: Allow HTTP and HTTPS traffic
3. Note the External IP address

#### 2. Setup SSH Access

```bash
# Add your SSH key to GCP
# Go to: Compute Engine → Metadata → SSH KEYS → ADD SSH KEY

# Connect to server
ssh YOUR_USERNAME@SERVER_IP
```

#### 3. Install Docker and Docker Compose

```bash
# Update packages
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again
exit
ssh YOUR_USERNAME@SERVER_IP

# Verify Docker
docker --version
docker compose version
```

#### 4. Copy Project to Server

```bash
# On your local machine
cd /path/to/marketing_generator_work

# Copy project files (excluding virtual environments)
rsync -avz --exclude='.venv' --exclude='__pycache__' --exclude='.git' \
  ./ YOUR_USERNAME@SERVER_IP:~/projects/marketing_generator/
```

#### 5. Start MongoDB

```bash
# On server
cd ~/projects/marketing_generator

# Start MongoDB using docker-compose
docker compose up -d mongodb

# Wait 10 seconds
sleep 10

# Verify MongoDB is running
docker ps | grep mongodb
```

#### 6. Install Python 3.11 and Poetry

```bash
# Install Python 3.11
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Verify Python version
python3.11 --version

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH (add to ~/.bashrc for persistence)
export PATH="/home/$USER/.local/bin:$PATH"

# Verify Poetry
poetry --version
```

#### 7. Install System Libraries for WeasyPrint (PDF Generation)

```bash
# Install required system libraries for WeasyPrint
sudo apt-get update
sudo apt-get install -y \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libgdk-pixbuf2.0-0 \
  libffi-dev \
  libcairo2 \
  libpangoft2-1.0-0

# These libraries are required for PDF generation functionality
```

#### 8. Install Python Dependencies

```bash
cd ~/projects/marketing_generator

# Configure Poetry to use Python 3.11
poetry env use python3.11

# Install dependencies (this may take 5-10 minutes)
poetry install --no-root
```

#### 9. Configure Environment Variables

```bash
# Update MongoDB connection string in .env
cd ~/projects/marketing_generator

# Edit .env file to use localhost for MongoDB
sed -i 's|CONNECTION_STRING_MONGO=.*|CONNECTION_STRING_MONGO=mongodb://admin:password123@localhost:27017/marketing_db?authSource=admin|' .env

# Verify
grep CONNECTION_STRING_MONGO .env
```

#### 10. Load Templates into MongoDB

```bash
cd ~/projects/marketing_generator

# Run seeding script
poetry run python seeding_scripts/insert_tempaltes.py

# Should output: "Templates inserted successfully!"
```

#### 11. Start Streamlit Application

```bash
cd ~/projects/marketing_generator

# Start Streamlit in background
nohup poetry run streamlit run Home.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &

# Wait a few seconds
sleep 5

# Check logs
tail -20 streamlit.log

# Should see: "You can now view your Streamlit app in your browser. URL: http://0.0.0.0:8501"
```

#### 12. Configure GCP Firewall

1. Go to **GCP Console** → **VPC network** → **Firewall** → **CREATE FIREWALL RULE**
2. Configure:
   - **Name**: `allow-streamlit-8501`
   - **Direction**: Ingress
   - **Action on match**: Allow
   - **Targets**: All instances in the network
   - **Source IPv4 ranges**: `0.0.0.0/0`
   - **Protocols and ports**: tcp:8501
3. Click **CREATE**

#### 13. Access Application

Open in browser: `http://YOUR_SERVER_IP:8501`

### Management Commands

#### Check Application Status

```bash
# Check if Streamlit is running
ssh YOUR_USERNAME@SERVER_IP "ps aux | grep streamlit | grep -v grep"

# Check MongoDB status
ssh YOUR_USERNAME@SERVER_IP "docker ps | grep mongodb"

# View Streamlit logs
ssh YOUR_USERNAME@SERVER_IP "tail -f ~/projects/marketing_generator/streamlit.log"

# View MongoDB logs
ssh YOUR_USERNAME@SERVER_IP "docker logs mongodb --tail 50"
```

#### Restart Streamlit

```bash
# Stop Streamlit
ssh YOUR_USERNAME@SERVER_IP "pkill -f 'streamlit run'"

# Start Streamlit again
ssh YOUR_USERNAME@SERVER_IP "cd ~/projects/marketing_generator && export PATH=\"/home/$USER/.local/bin:\$PATH\" && nohup poetry run streamlit run Home.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &"
```

#### Update Application Code

```bash
# On local machine: copy updated files
cd /path/to/marketing_generator_work
rsync -avz --exclude='.venv' --exclude='__pycache__' --exclude='.git' \
  ./ YOUR_USERNAME@SERVER_IP:~/projects/marketing_generator/

# On server: restart Streamlit
ssh YOUR_USERNAME@SERVER_IP "pkill -f 'streamlit run' && cd ~/projects/marketing_generator && export PATH=\"/home/$USER/.local/bin:\$PATH\" && nohup poetry run streamlit run Home.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &"
```

#### MongoDB Management

```bash
# Connect to MongoDB shell
ssh YOUR_USERNAME@SERVER_IP "docker exec -it mongodb mongosh -u admin -p password123 --authenticationDatabase admin"

# Inside MongoDB shell:
use marketing_db
show collections
db.content_templates.countDocuments()
db.campaigns.find().pretty()

# Backup MongoDB data
ssh YOUR_USERNAME@SERVER_IP "docker exec mongodb mongodump -u admin -p password123 --authenticationDatabase admin --out /tmp/backup"

# Restore MongoDB data
ssh YOUR_USERNAME@SERVER_IP "docker exec mongodb mongorestore -u admin -p password123 --authenticationDatabase admin /tmp/backup"
```

### Optional: Setup Systemd Service for Auto-Start

To automatically start Streamlit on server boot:

```bash
ssh YOUR_USERNAME@SERVER_IP

# Create systemd service file
sudo tee /etc/systemd/system/streamlit.service << 'EOF'
[Unit]
Description=Streamlit Marketing Generator
After=network.target docker.service

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/projects/marketing_generator
Environment="PATH=/home/YOUR_USERNAME/.local/bin:/usr/bin"
ExecStart=/home/YOUR_USERNAME/.local/bin/poetry run streamlit run Home.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl start streamlit

# Check status
sudo systemctl status streamlit

# View logs
sudo journalctl -u streamlit -f
```

### Troubleshooting

#### Application Not Starting

```bash
# Check Python version
ssh YOUR_USERNAME@SERVER_IP "python3.11 --version"

# Check Poetry installation
ssh YOUR_USERNAME@SERVER_IP "poetry --version"

# Reinstall dependencies
ssh YOUR_USERNAME@SERVER_IP "cd ~/projects/marketing_generator && poetry install --no-root"

# Check for errors in logs
ssh YOUR_USERNAME@SERVER_IP "tail -100 ~/projects/marketing_generator/streamlit.log"
```

#### MongoDB Connection Issues

```bash
# Check MongoDB is running
ssh YOUR_USERNAME@SERVER_IP "docker ps | grep mongodb"

# Check MongoDB logs
ssh YOUR_USERNAME@SERVER_IP "docker logs mongodb --tail 50"

# Restart MongoDB
ssh YOUR_USERNAME@SERVER_IP "cd ~/projects/marketing_generator && docker compose restart mongodb"

# Test connection
ssh YOUR_USERNAME@SERVER_IP "docker exec mongodb mongosh -u admin -p password123 --authenticationDatabase admin --eval 'db.runCommand({ ping: 1 })'"
```

#### Port Not Accessible

```bash
# Check if port is listening
ssh YOUR_USERNAME@SERVER_IP "sudo ss -tulpn | grep 8501"

# Check GCP firewall rules
# Go to: GCP Console → VPC network → Firewall
# Ensure rule "allow-streamlit-8501" exists with tcp:8501 allowed

# Check if UFW is blocking (should be inactive)
ssh YOUR_USERNAME@SERVER_IP "sudo ufw status"
```

#### WeasyPrint / PDF Generation Errors

If you see errors like `cannot load library 'libpango-1.0-0'`:

```bash
# Install required system libraries
ssh YOUR_USERNAME@SERVER_IP "sudo apt-get update && sudo apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev libcairo2 libpangoft2-1.0-0"

# Restart Streamlit
ssh YOUR_USERNAME@SERVER_IP "pkill -f 'streamlit run' && cd ~/projects/marketing_generator && export PATH=\"/home/\$USER/.local/bin:\$PATH\" && nohup poetry run streamlit run Home.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &"
```

#### Out of Memory

```bash
# Check memory usage
ssh YOUR_USERNAME@SERVER_IP "free -h"

# Check Docker memory usage
ssh YOUR_USERNAME@SERVER_IP "docker stats --no-stream"

# If needed, upgrade server to e2-standard-2 (8GB RAM) or higher
```

### Milvus Setup (Optional - for RAG)

By default, Milvus is disabled. To enable RAG functionality:

1. Uncomment Milvus services in `docker-compose.yml`:
   - `milvus-etcd`
   - `milvus-minio`
   - `milvus-standalone`

2. Update `.env` with Milvus connection string:
   ```env
   CONNECTION_STRING_MILVUS=http://root:Milvus@localhost:19530
   ```

3. Start Milvus:
   ```bash
   docker compose up -d milvus-etcd milvus-minio milvus-standalone
   ```

4. Restart Streamlit application

### Security Considerations

**Important:** The current setup is for development/testing. For production:

1. **Use HTTPS**: Setup nginx with Let's Encrypt SSL certificate
2. **Restrict Access**: Limit firewall rules to specific IP ranges
3. **Secure MongoDB**: Use strong passwords and enable authentication
4. **Environment Variables**: Use secret management (GCP Secret Manager)
5. **Regular Updates**: Keep system packages and Python dependencies updated
6. **Backups**: Setup automated backups for MongoDB data

### Cost Optimization

**Current Configuration (e2-standard-2):**
- ~$50-60/month (running 24/7)

**To Reduce Costs:**
1. Stop server when not in use: `gcloud compute instances stop INSTANCE_NAME`
2. Use preemptible instances (can be stopped by GCP, ~70% cheaper)
3. Use e2-medium instead (4GB RAM, ~$25-30/month)
4. Setup auto-shutdown script for off-hours

### Monitoring

```bash
# Check disk usage
ssh YOUR_USERNAME@SERVER_IP "df -h"

# Check CPU and memory
ssh YOUR_USERNAME@SERVER_IP "top -bn1 | head -20"

# Check application uptime
ssh YOUR_USERNAME@SERVER_IP "ps -eo pid,etime,comm | grep streamlit"

# Check Docker container stats
ssh YOUR_USERNAME@SERVER_IP "docker stats --no-stream"
```

---

## Additional Notes

- **Milvus**: Optional vector database for RAG functionality. If `CONNECTION_STRING_MILVUS` is not set in `.env`, the application will work without RAG.
- **Development Mode**: Application is running directly on server (not in Docker) for easier development and log access.
- **Production Mode**: For production, consider containerizing the entire stack or using managed services.