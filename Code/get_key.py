from openai import AzureOpenAI

def get_key():
    with open('./key.txt', 'r') as f:
        return tuple(map(str.strip,f.readlines()))
    
def get_client():
    api_key,api_version,azure_endpoint = get_key()
    client = AzureOpenAI(
    api_key = api_key,  
    api_version = api_version,
    azure_endpoint = azure_endpoint
    )
    return client
    
