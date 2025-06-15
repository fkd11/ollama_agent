import weaviate
from weaviate.classes.config import Configure, Property, DataType

class WeaviateHandler:

    def __init__(self,client):
        self.client = client

    def create_collection_meta(self, collection_name):
        if not self.client.schema.contains_class(collection_name):
            client.collections.create(
                collection_name,
                vectorizer_config=[
                    Configure.NamedVectors.text2vec_ollama(
                        name="general_vector",
                        # source_properties=["title"],
                        api_endpoint="http://host.docker.internal:11434",  # or "http://ollama:11434" if both in Docker
                        model="dengcao/Qwen3-Embedding-0.6B:F16",
                    )
                ],
                generative_config=Configure.Generative.ollama(
                    api_endpoint="http://host.docker.internal:11434",
                    model="qwen3:0.6b",
                ),
                inverted_index_config=Configure.inverted_index(
                    bm25_b=0.7,   # Set the 'b' parameter
                    bm25_k1=1.25  # Set the 'k1' parameter
                ),
                properties=[
                    Property(name="title",data_type=DataType.TEXT),
                    Property(name="abstract",data_type=DataType.TEXT),
                    Property(name="authors",data_type=DataType.TEXT_ARRAY, skip_vectorization=True),
                    Property(name="journal",data_type=DataType.TEXT, skip_vectorization=True),
                    Property(name="volume",data_type=DataType.TEXT, skip_vectorization=True),
                    Property(name="issue",data_type=DataType.TEXT, skip_vectorization=True),
                    Property(name="pages",data_type=DataType.TEXT, skip_vectorization=True),
                    Property(name="title",data_type=DataType.TEXT, skip_vectorization=True),
                    Property(name="year",data_type=DataType.TEXT, skip_vectorization=True),
                    Property(name="doi",data_type=DataType.TEXT, skip_vectorization=True),
                    Property(name="keywords",data_type=DataType.TEXT_ARRAY),

                    Property(name="file_path",data_type=DataType.TEXT, skip_vectorization=True),
              ],
            )

            # chunk class
            client.collections.create(
                collection_name,
                vectorizer_config=[
                    Configure.NamedVectors.text2vec_ollama(
                        name="general_vector",
                        # source_properties=["title"],
                        api_endpoint="http://host.docker.internal:11434",  # or "http://ollama:11434" if both in Docker
                        model="dengcao/Qwen3-Embedding-0.6B:F16",
                    )
                ],
                generative_config=Configure.Generative.ollama(
                    api_endpoint="http://host.docker.internal:11434",
                    model="qwen3:0.6b",
                ),
                inverted_index_config=Configure.inverted_index(
                    bm25_b=0.7,   # Set the 'b' parameter
                    bm25_k1=1.25  # Set the 'k1' parameter
                ),
                properties=[
                    Property(name="parent_paper",data_type=DataType.TEXT),
                    Property(name="chunk_id",data_type=DataType.TEXT),
                    Property(name="chunk_index",data_type=DataType.INT),
                    # Property(name="section",data_type=DataType.TEXT),
                    Property(name="related_chunk_ids",data_type=DataType.TEXT),
                    Property(name="usage_count",data_type=DataType.TEXT),
                    Property(name="ingestion_date",data_type=DataType.TEXT),
                ],
            )
            
            print(f"Collection '{collection_name}' created.")
        else:
            print(f"Collection '{collection_name}' already ollamaollamaexists.")
    


    def delete_collection(self, collection_name):
        if client.collections.get(collection_name).exists():
            self.client.collections.delete(collection_name)
            print(f"Collection '{collection_name}' deleted.")
        else:
            print(f"Collection '{collection_name}' does not exist.")



with weaviate.connect_to_local() as client:
    weaviate_hndl = WeaviateHandler(client)
    # weaviate_hndl.delete_collection("MultiTenancyCollection")
    weaviate_hndl.create_collection("Scholar")
    
