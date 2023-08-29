import os
from langchain.memory import ConversationSummaryBufferMemory
from langchain.llms.bedrock import Bedrock
from langchain.chains import ConversationChain
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth

def get_llm():
    
    # anthropic inference arguments
    model_kwargs =  { 
        "max_tokens_to_sample": 512,
        "temperature": 0.1, 
        #"top_k": 250, 
        "top_p": 0.9, 
        "stop_sequences": ["\n\nHuman:"]
    }
    
    llm = Bedrock(
        credentials_profile_name=os.environ.get("BWB_PROFILE_NAME"), #sets the profile name to use for AWS credentials (if not the default)
        region_name=os.environ.get("BWB_REGION_NAME"), #sets the region name (if not the default)
        endpoint_url=os.environ.get("BWB_ENDPOINT_URL"), #sets the endpoint URL (if necessary)
        model_id="anthropic.claude-v2", #use the Anthropic Claude model
        model_kwargs=model_kwargs) #configure the properties for Claude
    
    return llm


def get_memory(): #create memory for this chat session
    
    #ConversationSummaryBufferMemory requires an LLM for summarizing older messages
    #this allows us to maintain the "big picture" of a long-running conversation
    llm = get_llm()
    
    memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=1024) #Maintains a summary of previous messages
    
    return memory
    
def get_OSSConn(): #create a context based on OpenSearch Vector Index
    # Connect to OpenSearch
    auth = ("master","Semantic123!")
    aos_client = OpenSearch(
        hosts = [{'host': os.environ.get("BWB_AOS_DOMAIN_ENDPOINT"), 'port': 443}],
        http_auth = auth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    return aos_client
    
def get_Context(input_query, aos_client): # create relevant context for LLM
    
    query={
      "_source": {
            "exclude": [ "pdf_text_vector" ]
        },
      "size": 30,
      "query": {
        "neural": {
          "pdf_text_vector": {
            #"query_text": "what are the features of API gateway?",
            #"query_text": "Who uses API gateway?",
            #"query_text":  'What are the cloudwatch metrics for monitoring websocket APIs?',
            "query_text": input_query,
            "model_id": 'qk3fLooBGSulaPZDmnJX',
            "k": 30
          }
        }
      }
    }
    
    relevant_documents = aos_client.search(
        body = query,
        index = 'nlp_awsdocs'
    )
    
    context = " "
    for i, rel_doc in enumerate(relevant_documents["hits"]["hits"]):
        # print('---')
        context += relevant_documents["hits"]["hits"][i]["_source"]["pdf_text"]
    
    return context

def get_chat_response(input_text, memory): #chat client function
    
    llm = get_llm()
    aos_client = get_OSSConn()
    context = get_Context(input_text, aos_client)
    
    prompt_data_claude = f"""Human: Answer the question based only on the information provided. If the answer is not in the context, say "I don't know, answer not found in the documents. Provide quote from the document.
        <context>
        {context}
        </context>
        <question>
        {input_text}
        </question>
        Assistant:"""
    
    # conversation_with_summary = ConversationChain( #create a chat client
    #     llm = llm, #using the Bedrock LLM
    #     memory = memory, #with the summarization memory
    #     verbose = True #print out some of the internal states of the chain while running
    # )
    
    # chat_response = conversation_with_summary.predict(input=input_text) #pass the user message and summary to the model
    chat_response = llm(prompt_data_claude)
    
    return chat_response