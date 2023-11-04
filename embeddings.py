import os
import tempfile
import time
import sys
import logging
import openai


from llama_index import SimpleDirectoryReader, GPTVectorStoreIndex
from llama_index import ServiceContext
from llama_index.llms import OpenAI
from llama_index.embeddings import GradientEmbedding, HuggingFaceEmbedding

from llama_index.node_parser import SimpleNodeParser
from llama_index import SimpleDirectoryReader, VectorStoreIndex, ServiceContext, StorageContext
from llama_index.storage.docstore import SimpleDocumentStore

from legalease_environment import openai_key #your key here from file 

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

os.environ["OPENAI_API_KEY"]=openai_key

# Reading Document
def generate_embeddings(ls: list):
    
    for name in ls:
        documents = SimpleDirectoryReader(input_files=[f"{name}.pdf"]).load_data()

        # Parsing Document into nodes
        node_parser = SimpleNodeParser.from_defaults(chunk_size=1024, chunk_overlap=20)
        service_context = ServiceContext.from_defaults(node_parser=node_parser)
        nodes = node_parser.get_nodes_from_documents(documents)

        # Creating index from nodes
        index = VectorStoreIndex(nodes, service_context=service_context, show_progress=True)

        # Set the index id
        index.set_index_id("vector_index")

        # Storing the generated embeddings from index
        index.storage_context.persist(persist_dir=f"{name}")

names = ["sga","ica","sra","upra","tpa"]

generate_embeddings(names)