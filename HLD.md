## 1. High-Level Architecture Overview

This document explains the architectural design for a distributed document chunking and retrieval augmented generation (RAG) system that efficiently processes large volumes of documents while enabling scalability and parallelism.

![Architecture Diagram](https://github.com/ptbdnr/rag/blob/main/static/hld.mermaid.png)

This high-level design provides a scalable, efficient framework for document chunking in RAG systems. The architecture balances performance, scalability, and quality while addressing key operational challenges. By leveraging distributed processing and intelligent chunking strategies, the system can efficiently handle large document collections while providing high-quality results for downstream retrieval and generation tasks.

## 2. Core Components

### 2.1 API Gateway
The API layer serves as the entry point for document processing requests and query handling. It manages authentication, rate limiting, and request routing.

### 2.2 Workflow Orchestrator
Coordinates the entire document processing pipeline, ensuring tasks are executed in the correct order while maintaining parallel processing. The orchestrator tracks job status and handles failures.

### 2.3 Document Loader
Responsible for retrieving documents from various sources (URLs, uploads) and preparing them for processing. Supports multiple document formats. Output is saved in an object store.

### 2.4 OCR Service
Extracts text from image-based documents or (scanned) PDFs.

### 2.5 Document Splitter
The core chunking component that divides documents into meaningful segments while preserving context. Supports multiple chunking strategies: fix and semantic. The output is saved in a text database.

### 2.6 Encoder
Generates vector embeddings for document chunks using an embedding model and injects them into the (text and) vector database.

### 2.7 Object Store
Persistent storage for original documents and processed chunks, enabling retrieval and reprocessing when needed.

### 2.8 Text and Vector Database
Stores document chunks and their vector representations with metadata for efficient retrieval.

### 2.9 Support Services
- **Keys**: Secure storage for Identify, API keys and credentials
- **Monitor**: Observability and logging infrastructure
- **Container Registry**: Storage for containerized services

## 3. Design Decisions

### 3.1 Microservices Architecture
- **Decision**: Implement each major component as a separate microservice.
- **Rationale**: Enables independent scaling of components based on workload characteristics. For example, document loading (with OCR processing) may require more resources and time than splitting text to chunks.
- **Impact**: Improved resource utilization and resilience, at the cost of increased system complexity.

### 3.2 Chunking Strategy Selection
- **Decision**: Dynamic chunking strategy selection based on document type and content.
- **Rationale**: Different document types (technical manuals, articles, code) require different chunking approaches to preserve semantic meaning.
- **Impact**: Improved retrieval quality with contextually appropriate chunks, at the cost of more complex preprocessing logic.

### 3.3 Vector Database Selection
- **Decision**: Use a combined text and vector database rather than a specialized vector database.
- **Rationale**: Optimized for keyword and similarity searches, supporting hybrid search while fortifying data lienage.
- **Impact**: Superior data consistency lexical/semantic/hybrid searches at scale, with potential increased operational complexity and risk of embedding model lock-in.

### 3.4 Cloud-Native Infrastructure
- **Decision**: Deploy on cloud infrastructure with containerization.
- **Rationale**: Leverage managed services for scaling, monitoring, and reliability.
- **Impact**: Reduced operational overhead and improved scalability, with cloud provider lock-in considerations.

## 4. Bottlenecks and Limitations

### 4.1 Processing Bottlenecks

- **OCR Processing**: Image-based document processing is significantly slower than text-based document processing.
  - *Mitigation*: Separate processing queues with priority settings and dedicated resources for OCR tasks.

- **Embedding Generation**: Vector encoding is computationally intensive and can become a bottleneck when processing large volumes of documents.
  - *Mitigation*: Self-hosting embedding models, batch processing, GPU acceleration, and caching of embedding results.

- **Database Write Operations**: High-volume chunk storage operations can overload the text and vector database.
  - *Mitigation*: Bulk operations, write batching, and database scaling strategies.

### 4.2 Scaling Limitations

- **Stateful Components**: Services that maintain state are harder to scale horizontally.
  - *Mitigation*: Minimize state in processing services, leverage external state stores.

- **Resource Contention**: Multiple tenants competing for the same resources can cause performance degradation.
  - *Mitigation*: Resource quotas and prioritization mechanisms.

### 4.3 Technical Limitations

- **Chunk Size Trade-offs**: Smaller chunks improve retrieval precision but reduce context, while larger chunks preserve context but may reduce retrieval precision.
  - *Mitigation*: Hierarchical chunking strategies and overlapping chunks to preserve context.

- **Embedding Model Constraints**: Fixed context windows in embedding models limit the size of processable chunks.
  - *Mitigation*: Optimized chunking that respects model limitations while preserving semantic meaning.

- **Cold Start Problems**: On-demand scaling can introduce latency during traffic spikes.
  - *Mitigation*: Predictive scaling, warm pools for critical services, and queue-based workload smoothing.

## 5. Multi-Tenant Support

The system supports multi-tenant operations through:

- **Tenant Isolation**: Logical separation of data with tenant-specific partitions.
- **Resource Quotas**: Configurable limits on processing resources, storage, and API calls per tenant.
- **Custom Configurations**: Tenant-specific chunking strategies, models, and processing parameters.
- **Access Control**: Fine-grained permissions and authentication at the tenant level.

## 6. Monitoring and Observability

The system includes comprehensive monitoring features:

- **Processing Metrics**: Tracking of document volume, processing time, and error rates.
- **Resource Utilization**: Hardware and storage usage across the system (subject to cloud provider / on-prem infrastucture).
- **End-to-End Tracing**: Request tracking for debugging.
- **Alerting**: Notification of system issues or unusual patterns.

## 7. Future Enhancements

- **Domain-Specific Chunking**: Specialized chunking strategies for specific document domains (legal, medical, technical).
- **Adaptive Resource Allocation**: Machine learning-based prediction of resource needs based on document characteristics.
- **Enhanced Metadata Extraction**: Improved automatic tagging and categorization of document content.
- **Cross-Lingual Support**: Processing and retrieval across multiple languages.
- **Incremental Processing**: Efficient handling of document updates and changes.

