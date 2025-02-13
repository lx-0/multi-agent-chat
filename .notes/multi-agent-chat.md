#

##

```
Please create a multi agent demo using "PydanticAI" @PydanticAI_Docs and Chainlit UI @ChainLit . Note the difference between PydanticAI and Pydantic - we will use PydanticAI!! The agents shall be using the supervisor agent approach. I need to see the interaction between the agents in the UI when occurring (streaming?). Use best practices for the supervisor agent approach . For Multi-Agent, use best practice from: @https://ai.pydantic.dev/multi-agent-applications/#agent-delegation .


Please create a multi agent demo with these STRICT requirements:

1. USE ONLY PydanticAI (https://ai.pydantic.dev/) - DO NOT CONFUSE WITH REGULAR PYDANTIC
2. USE ONLY documented features from PydanticAI docs @PydanticAI_Docs
3. USE Chainlit UI for visualization @ChainLit
4. VERIFY all imports and decorators against PydanticAI documentation before implementing
5. DO NOT USE PYDANTIC!!! JUST PydanticAI!!!!

The agents shall use the supervisor agent approach. I need to see the interaction between the agents in the UI when occurring (streaming?). For Multi-Agent, use best practice from: @https://ai.pydantic.dev/multi-agent-applications/#agent-delegation .

DO NOT RUSH INTO THE IMPLEMENTATION. THINK STEP BY STEP BEFORE WRITING ANY CODE.
```

Resources

ReAct: <https://huggingface.co/blog/open-source-llms-as-agents>

Supervisor Agent Approach: <https://medium.com/@sahin.samia/multi-agent-ai-systems-foundational-concepts-and-architectures-ece9f8859302>

CrewAI

##

Hotel Service Coordinator
Supervisor Agent: Guest Service Manager
Specialist Agents:
Room Service Agent: Handles food/amenity requests
Concierge Agent: Provides local recommendations
Maintenance Agent: Coordinates room issues
Real Benefits: "Multilingual, 24/7, and easily accessible to guests"

**Supervisor Agent (Concierge Manager)**

```plaintext
- Primary role: Coordinate guest requests and delegate to specialist agents
- Capabilities:
  - Request classification
  - Priority management
  - Service coordination
  - Final response synthesis
```

**Specialist agents**

```plaintext
a) Room Service Agent
   - Handle food and beverage orders
   - Manage dining reservations
   - Track order status
   - Dietary requirements

b) Amenity Agent
   - Housekeeping requests
   - Extra towels/supplies
   - Room maintenance issues
   - Special accommodations

c) Concierge Agent
   - Local recommendations
   - Transportation booking
   - Activity reservations
   - Directions and maps
```

**Example interaction flow**

```plaintext
Guest: "I need extra towels, and could you recommend a good Italian restaurant nearby for dinner?"

1. Supervisor Agent:
   - Analyzes request
   - Identifies two tasks: housekeeping and restaurant recommendation
   - Delegates to appropriate agents

2. Amenity Agent:
   - Processes towel request
   - Schedules delivery
   - Updates room status

3. Concierge Agent:
   - Searches local restaurants
   - Checks ratings and availability
   - Prepares booking options

4. Supervisor Agent:
   - Combines responses
   - Delivers unified response to guest
```
