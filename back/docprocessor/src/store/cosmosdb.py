import os
import logging
from typing import TYPE_CHECKING, Optional

import dotenv

from azure.cosmos import exceptions
from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos.container import ContainerProxy
from azure.cosmos.database import DatabaseProxy

import dotenv
dotenv.load_dotenv('.env.local')

COSMOSDB_NOSQL_HOST = os.getenv("COSMOSDB_NOSQL_HOST")
COSMOSDB_NOSQL_KEY = os.getenv("COSMOSDB_NOSQL_KEY")
COSMOSDB_DATABASE_ID = os.getenv("COSMOSDB_DATABASE_ID")
COSMOSDB_CONTAINER_ID = os.getenv("COSMOSDB_CONTAINER_ID")
COSMOSDB_PARTITION_KEY = "/tenantId"
ALLOWED_SELECT_FIELDS = ['id', 'tenantId', 'documentId', 'text', 'vector']

class CosmosDB:
    """CosmosDB data store."""

    database_id: str
    container_id: str
    partition_key: str

    client: CosmosClient
    db: DatabaseProxy
    container: ContainerProxy

    def __init__(self) -> None:
        """Initialize."""
        # Configure
        self.database_id = COSMOSDB_DATABASE_ID
        self.container_id = COSMOSDB_CONTAINER_ID
        self.partition_key = COSMOSDB_PARTITION_KEY

        # Logging
        logging.info("CosmosDB: %s", COSMOSDB_NOSQL_HOST)
        logging.info("CosmosDB: %s", COSMOSDB_DATABASE_ID)
        logging.info("CosmosDB: %s", COSMOSDB_CONTAINER_ID)
        logging.info("CosmosDB: %s", COSMOSDB_PARTITION_KEY)

        # Initialize the client
        self.client = CosmosClient(
            url=COSMOSDB_NOSQL_HOST,
            credential={"masterKey": COSMOSDB_NOSQL_KEY},
            user_agent="CosmosDBPython",
            user_agent_overwrite=True,
        )
        self.db = None
        self.container = None

    def create(
        self,
        indexing_policy: Optional[dict] = None,
        vector_embedding_policy: Optional[dict] = None,
        offer_throughput: Optional[int] = None,
        drop_old_database: bool = False,
        drop_old_container: bool = False,
    ) -> ContainerProxy:
        
        self.client = CosmosClient(
            url=COSMOSDB_NOSQL_HOST,
            credential={"masterKey": COSMOSDB_NOSQL_KEY},
            user_agent="CosmosDBPython",
            user_agent_overwrite=True,
        )
        """Create a container."""
        if self.client is None:
            msg = "CosmosDB client not found"
            raise ValueError(msg)
        if self.db is None:
            if drop_old_database:
                self.client.delete_database(id=self.database_id)
            try:
                self.db = self.client.create_database(id=self.database_id)
            except exceptions.CosmosResourceExistsError:
                self.db = self.client.get_database_client(database=self.database_id)
        if self.container is None:
            if drop_old_container:
                self.db.delete_container(id=self.container_id)
            try:
                self.container = self.db.create_container(
                    id=self.container_id,
                    partition_key=PartitionKey(path=self.partition_key),
                    indexing_policy=indexing_policy,
                    vector_embedding_policy=vector_embedding_policy,
                    offer_throughput=offer_throughput,
                )
            except exceptions.CosmosResourceExistsError:
                self.container = self.db.get_container_client(
                    container=self.container_id,
                )
        return self.container

    def upsert(self, payload: dict) -> None:
        """Upsert an item."""
        
        if "id" not in payload:
            msg = "The field 'id' is required in record."
            raise ValueError(msg)
        return self.container.upsert_item(body=payload)
    
    def find(self, filter: Optional[dict]) -> list:
        """Find items."""
        self.create()
        validated_fields = ", ".join("c." + f for f in ALLOWED_SELECT_FIELDS)
        query = "SELECT " + validated_fields + " FROM c"
        parameters = []
        conditions = []
        if filter:
            for k, v in filter.items():
                if v:
                    param_name = f"@{k}"
                    conditions.append(f"c.{k} = {param_name}")
                    parameters.append({"name": param_name, "value": v})
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        return list(self.container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
        ))