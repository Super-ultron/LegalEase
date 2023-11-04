import os
import logging
import sys
import tiktoken
import re
import templates as tm

from llama_index.callbacks import CallbackManager, TokenCountingHandler
from llama_index import StorageContext, load_index_from_storage, SummaryIndex, ServiceContext
from llama_index.indices.vector_store.retrievers.retriever import VectorIndexRetriever
from llama_index.vector_stores.types import VectorStoreQueryMode
from llama_index.indices.vector_store import VectorStoreIndex
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.schema import IndexNode
from llama_index.retrievers import RecursiveRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.response_synthesizers import get_response_synthesizer
from llama_index.agent import OpenAIAgent
from llama_index.llms import OpenAI as op1

from typing import List, Union

from legalease_environment import openai_key, openai_keyp

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

os.environ['OPENAI_API_KEY'] = openai_key

llm = op1(temperature=0, model='gpt-3.5-turbo')
service_context = ServiceContext.from_defaults(llm=llm)

def remove_formatting(output):
    output = re.sub('\[[0-9;m]+', '', output)  
    output = re.sub('\', '', output)  
    output = re.sub(r'\[+', '', output)  
    output = re.sub(r'\]+', '', output)  
    output = re.sub(r'^\s*\n', '', output)  
    output = re.sub(r'\n+', '\n', output)  
    output = re.sub(r'Generated (\d+) sub questions\.', r'\nGenerated \1 sub questions.', output)  
    output = output.strip()
    return output


def preprocessing():
    names = ["The Indian Contract Act, 1872","The Sales of Goods Act, 1930","The Specific Relief Act, 1963","The Transfer of Property Act, 1882", "The Uttar Pradesh Urban Buildings (Regulation of Letting, Rent and Eviction) Act, 1972"]
    descriptions = ["The go-to document for Contract Rules. The Indian Contract Act, 1872 is a fundamental legal framework in India that governs the formation and enforcement of contracts, defining the rules and principles that underlie agreements between parties in various transactions.", "The go-to document for rules related to sale of goods. The Sales of Goods Act, 1930 is an Indian legislation that governs the sale and purchase of goods, outlining the rights and obligations of both buyers and sellers in commercial transactions.", "The go-to document for Relief Rules. The Specific Relief Act, 1963 is an Indian legal statute that governs the remedies available for the enforcement of civil rights and obligations, emphasizing the specific performance of contracts as a primary remedy.", "The go-to document for Rules for transferring property and its rights. The Transfer of Property Act, 1882 is a legal statute in India that governs the transfer of property from one person to another. It defines various types of property transactions, including sales, mortgages, leases, and gifts, and sets out the legal rules and procedures for such transfers.", "The go-to document for Rules and Regulations for Rent in Uttar Pradesh. The Uttar Pradesh Urban Buildings Act of 1972 regulates the rental and eviction of urban properties in the Indian state of Uttar Pradesh"]
    temp = ['ica', 'sga', 'sra', 'tpa', 'upra']

    agents = {}

    for n,x in enumerate(temp):
        storage_context = StorageContext.from_defaults(persist_dir=x)
        
        vector_index = load_index_from_storage(storage_context=storage_context, index_id="vector_index")
        summary_index = load_index_from_storage(storage_context=storage_context, index_id="vector_index")
        
        vector_query_engine = vector_index.as_query_engine()
        list_query_engine = summary_index.as_query_engine()
        
        query_engine_tools = [
            QueryEngineTool(
                query_engine = vector_query_engine,
                metadata = ToolMetadata(name = temp[n],description= descriptions[n])
            ),
            QueryEngineTool(
                query_engine = list_query_engine,
                metadata =  ToolMetadata(name = temp[n], description= descriptions[n])
            )
        ]
        function_llm = op1(model="gpt-3.5-turbo-0613")
        agent = OpenAIAgent.from_tools(
            query_engine_tools,
            llm=function_llm,
            verbose=True,
        )
        agents[x] = agent

    nodes = []
    for n,x in enumerate(names):
        act_summary = (
            f"This content contains Acts about {x}. "
            f"Use this index if you need to lookup specific facts about {x}.\n"
            "Do not use this index if you want to ." #Todo -> add the instructions here 
        )
        node = IndexNode(text=act_summary, index_id=temp[n])
        nodes.append(node)

    vector_index = VectorStoreIndex(nodes)
    vector_retriever = vector_index.as_retriever(similarity_top_k=1)

    recursive_retriever = RecursiveRetriever(
        "vector",
        retriever_dict={"vector": vector_retriever},
        query_engine_dict=agents,
        verbose=True,
    )

    response_synthesizer = get_response_synthesizer(
        # service_context=service_context,
        response_mode="compact",
    )
    query_engine = RetrieverQueryEngine.from_args(
        recursive_retriever,
        response_synthesizer=response_synthesizer,
        service_context=service_context,
    )

    tools = [
        Tool(
            name = "Llama-Index",
            func = query_engine.query,
            description = """Useful for when you want to extract content. 
            The input to this tool should be a complete English sentence. 
            Works best if you redirect the entire query back into this.""",
            return_direct = True
        )
    ]

    prompt = CustomPromptTemplate(
        template = tm.template1,
        tools = tools,
        input_variables = ["input", "intermediate_steps"]
    )

    output_parser = CustomOutputParser()

    llm = op2(temperature=0)
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    tool_names = [tool.name for tool in tools]
    agent = LLMSingleActionAgent(
        llm_chain = llm_chain, 
        output_parser = output_parser,
        stop = ["\nObservation"], 
        allowed_tools = tool_names
    )

    agent_chain = AgentExecutor.from_agent_and_tools(tools = tools, agent = agent, verbose = True)

    return agent_chain
  