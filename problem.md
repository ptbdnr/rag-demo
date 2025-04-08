# Problem statement 

Document Chunking for RAG System

## Part 1: High-Level Design

### Objective  

Implement a distributed document chunking service for RAG with parallelized processing capabilities.

Sample Data:
* some kithen whitegood manual
* non-English kitchen whitegood manual
* car manual
* tv manual

### Technical Components

Provide a high-level architecture diagram and description for the document chunking component, including the following elements: 

1. Distributed Processing: Ensure the system can process documents in parallel across multiple nodes to handle large-scale data efficiently. 
2. Chunking Algorithm: Define the approach for splitting documents into meaningful chunks. 
3. Load Distribution: Confirm that mechanisms is efficient for distribute workloads across available resources. 
4. Elastic Scaling: Design the system to scale dynamically based on workload demands. 
5. Observability Stack: Design observability features to track processing status, errors, and performance. 

### Multi-tenant Architecture

Implement tenant isolation.


## Part 2: Implementation 

Implement an AI assistant POC to handle queries

Sample Interaction: 

```yaml
Technician: "I've got a customer with an LG X7500 refrigerator. They're reporting error code C1 and saying the freezer isn't cooling properly though the refrigerator section seems fine."

AI Assistant: "Error code C1 on the LG X7500 typically indicates a defrost system malfunction. The freezer section not cooling properly while the refrigerator works is consistent with this diagnosis. First, check if there's excessive frost buildup on the evaporator coil. Have you inspected this area yet?"

Technician: "I opened the freezer panel and there's definitely significant ice buildup around the evaporator. Almost completely covered."

AI Assistant: "That confirms our diagnosis. You'll need to address the defrost system failure. First, disconnect power to the unit for safety. Then check the defrost heater for continuity using a multimeter. If the heater has continuity, the issue is likely with the defrost thermostat or control board. Can you test the heater?"

Technician: "Just tested the heater and it's showing an open circuit. Reading is infinite ohms."

AI Assistant: "That's our problem. The defrost heater has failed and needs replacement. For the LG X7500, you'll need part #DR-47890. Once installed, be sure to check the defrost thermostat as well since these components often fail together. Would you like instructions on removing and replacing the heater assembly?"

Technician: "No need, I've done these before. I'll get the part and replace it. Do you recommend any preventative maintenance while I'm in there?"

AI Assistant: "Good thinking. While the panel is open, clean the drain port at the bottom of the evaporator to prevent future blockages. Also inspect the defrost thermostat wiring for any signs of corrosion. The condenser coils should be cleaned if they appear dusty, as this model tends to accumulate debris there quickly."

Technician: "Just finished the replacement and everything's working correctly now. The system is cycling properly and error code is gone."

AI Assistant: "Excellent work. Remind the customer to avoid overpacking the freezer vents to prevent airflow restrictions that can accelerate frost buildup. If you encounter any further issues with this LG X7500 or other refrigerator models, I'm here to assist."
```
