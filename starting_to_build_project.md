Step 1: Give Cursor This Master Prompt

Create a new project folder and paste the following into Cursor Agent mode:

You are a senior AI systems architect and full-stack engineer.

Build a production-grade multi-agent village simulation called VillageVerse.

Tech Stack:

Backend:
- Python 3.12
- FastAPI
- LangGraph
- LangChain
- Ollama

Database:
- SQLite initially
- SQLAlchemy ORM

Frontend:
- React
- Vite
- TypeScript
- TailwindCSS

Architecture:

The simulation contains:

- 100-500 villagers
- Indian families
- Persistent memories
- Relationships
- Emotions
- Events
- Gossip
- Story feed

Prompt files already exist under:

configs/prompts/

Do NOT hardcode prompts.

Load prompts dynamically.

Create a modular architecture.

Folder structure:

backend/
frontend/
configs/
data/

Requirements:

1. LangGraph simulation workflow

World State
→ Event Generator
→ Agent Selector
→ Conversation Engine
→ Memory Manager
→ Relationship Manager
→ Emotion Engine
→ Gossip Engine
→ Story Feed Logger
→ Save State

2. Persistent Storage

Store:

- villagers
- families
- memories
- relationships
- conversations
- stories
- rumors

3. API Endpoints

GET /villagers
GET /villagers/{id}

GET /families

GET /stories

GET /stories/{id}

GET /locations

POST /simulation/tick

POST /simulation/run

4. Story Feed UI

Features:

- Infinite scroll
- Search
- Date filter
- Time filter
- Character filter
- Family filter
- Location filter
- Importance filter

5. Villager Profile UI

Display:

- memories
- friends
- rivals
- recent stories
- current emotion

6. Family Profile UI

Display:

- family tree
- members
- reputation
- wealth

7. Simulation Dashboard

Display:

- active villagers
- current events
- latest stories
- emotional trends

8. Build incrementally.

Generate code in phases.

Phase 1:

Backend architecture
Database models
Prompt loader
LangGraph skeleton

Stop after phase 1.
Wait for approval.
What Cursor Should Build First

Don't let it jump directly into UI.

First build:

backend/

├── app/
│   ├── models/
│   ├── graph/
│   ├── prompts/
│   ├── services/
│   ├── api/
│   └── database/
│
├── main.py
└── requirements.txt
After Cursor Finishes Phase 1

Tell Cursor:

Phase 1 approved.

Build Phase 2.

Implement:

- Villager model
- Family model
- Story model
- Memory model
- Relationship model

Create SQLAlchemy schemas.

Create migration support.

Generate sample seed data.

Stop after completion.
Then Phase 3
Build LangGraph nodes.

Create:

WorldStateNode

EventGeneratorNode

AgentSelectorNode

ConversationNode

MemoryNode

RelationshipNode

EmotionNode

GossipNode

StoryLoggerNode

Each node must load its prompt from configs/prompts.

Use Ollama via LangChain.

Stop after implementation.
Then Phase 4
Implement simulation engine.

Requirements:

- Tick-based simulation
- Run 1 tick
- Run N ticks
- Run continuously

Persist every change.

Generate stories.

Generate conversations.

Generate events.

Provide API endpoints.

Stop after completion.
Then Phase 5
Build React frontend.

Pages:

Dashboard

Story Feed

Villagers

Families

Locations

Search

Use FastAPI backend.

Create responsive UI.

Stop after completion.
Then Phase 6
Create Story Feed page.

Requirements:

Filter by:

- date
- time
- category
- villager
- family
- location
- importance

Show:

Title

Timestamp

Location

Participants

Summary

Read Full Story

Implement infinite scrolling.
Then Phase 7
Create simulation controls.

Buttons:

Run 1 Tick

Run 10 Ticks

Run 100 Ticks

Start Continuous Simulation

Pause Simulation

Display:

Current Day

Current Time

Population

Active Conversations

Latest Events
How You Should Proceed

Development order:

1. Backend Skeleton
2. Database Models
3. LangGraph Nodes
4. Simulation Engine
5. Story Feed
6. APIs
7. React UI
8. Optimization
9. Multi-threading
10. Large Population Scaling

Do not start with 500 villagers.

Start with:

families: 10
villagers: 40
active_agents_per_tick: 5

Once stable:

families: 50
villagers: 300
active_agents_per_tick: 15