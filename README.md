# RAG-Chunking: Distributed Document Processing for AI Assistants

[![License: GNU GPLv3](https://img.shields.io/badge/License-GPLv3-yellow.svg)](https://choosealicense.com/licenses/gpl-3.0/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A scalable, distributed system for document chunking and processing in Retrieval Augmented Generation (RAG) applications. This repository contains both the high-level architecture and a working implementation of an AI troubleshooting assistant powered by RAG.

## Overview

RAG-Chunking provides a comprehensive solution for:

- Efficient document ingestion and chunking
- Parallel processing of large document collections
- Semantic vector embedding generation
- Vector-based similarity search
- Intelligent query handling with context awareness

Perfect for building domain-specific AI assistants that can leverage technical documentation, manuals, and knowledge bases.

## Architecture

![Architecture Diagram](https://github.com/ptbdnr/rag/blob/main/static/rag-hld_v01.png)

The system consists of several key components:

- **Document Intake Service**: Processes documents from multiple sources
- **Document Splitter**: Intelligently chunks documents with semantic awareness
- **Embedding Generator**: Creates vector representations of document chunks
- **Vector Database**: Stores and indexes chunks for fast retrieval
- **Query Processor**: Handles user queries and retrieves relevant context
- **Response Generator**: Creates AI responses based on retrieved context

## Features

- ✅ **Parallel Processing**: Process documents concurrently for maximum throughput
- ✅ **Smart Chunking**: Preserve semantic meaning with intelligent document splitting
- ✅ **Scalable Architecture**: Add processing nodes to handle larger document volumes
- ✅ **Multi-Format Support**: Process PDFs, HTML, text files, and more
- ✅ **Conversation Context**: Maintain dialogue history for improved responses
- ✅ **Extensive Logging**: Comprehensive monitoring and observability

## Getting Started

### Prerequisites

- Azure account
- Python 3.10+

### Installation

```bash
# Clone the repository
git clone https://github.com/ptbdnr/rag.git
cd rag

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Quick Start

TODO

## Example Use Case: Appliance Troubleshooting Assistant

This repository includes a complete implementation of a troubleshooting assistant for household appliances. The assistant:

1. Processes technical service manuals and user guides
2. Understands error codes and common problems
3. Provides step-by-step troubleshooting instructions
4. Maintains conversation context for follow-up questions

See `examples/TODO` for a complete demonstration.

## Scalability

The system is designed for horizontal scaling:

- Each component can be deployed as a separate microservice
- Processing can be distributed across multiple nodes
- Document processing is parallelized for maximum throughput
- Supports multi-tenant operation with resource isolation

## License

This project is licensed under the GNU GPLv3 License - see the LICENSE file for details.
