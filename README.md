This repo is for building a chatbot using streamlit, bedrock and opensearch.
The architecture is using Retrieval Augmented Generation (RAG) where the LLM is using the related documents from the context to answer service specific queries.

This repo assumes you have a working Opensearch cluster and access to Bedrock Anthorpic claude v2 LLM

Pre-requisites:

1)
- Create an Opensearch cluster
- Setup neural plugin for vector embeddings
- Create a neural pipline
- Create an open search index
- Ingest service documents in Opensearch index
You can use the notebook in this repo to cover the above steps

2)
- Get access to bedrock and install dependencies (boto3, botocore, bedrock-sdk)
  Refer to this link: https://catalog.workshops.aws/building-with-amazon-bedrock/en-US/prerequisites/lab-setup
- Ensure you have access to Anthropic Claude v2 3P model.
- Titan Large will also work if you don't have access to Claude

3) Env Variables for the chatbot to work! 

- export BWB_REGION_NAME=`Region`
- export BWB_ENDPOINT_URL=`Bedrock Endpoint`
- export BWB_PROFILE_NAME=`profile for aws cli`
- export BWB_AOS_DOMAIN_ENDPOINT=`Opensearch Domain Endpoint`
