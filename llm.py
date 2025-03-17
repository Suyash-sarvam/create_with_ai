from dotenv import load_dotenv
import anthropic
import os 
from author import render_template
import os 
import json 
import uuid

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

async_client=anthropic.AsyncAnthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")

)
def get_completion(prompt,model_id):
    try:
        llm_config = {
                "max_tokens": 15000,
                "thinking":{
                    "type": "enabled",
                    "budget_tokens": 2000
                },
            }

        model_dict={"3-7":'claude-3-7-sonnet-20250219',"3-5":'claude-3-5-sonnet-20241022'}
        config_dict={"3-7":llm_config,"3-5":{"max_tokens":7000}}
        response=client.messages.create(
            model=model_dict[model_id],
            messages=[{"role":"user","content":prompt}],
            **config_dict[model_id]
        )
        if model_id=='3-5':
            return response.content[0].text
        else:
            return response
    except Exception as e:
        raise e 

def generate_agent_config(usecase_details):
    try:

        #savinf inputs 
        os.makedirs("configs",exist_ok=True)
        kwargs={
            "usecase_details":usecase_details
        }
        prompt=render_template("v2v.j2",**kwargs)

        llm_config = {
                "max_tokens": 15000,
                "thinking":{
                    "type": "enabled",
                    "budget_tokens": 2000
                },
            }
        final_response=""
        with client.messages.stream(
            model='claude-3-7-sonnet-20250219',
            messages=[{"role":"user","content":prompt}],
            **llm_config

        ) as stream:
            for event in stream:
                if event.type=="content_block_delta":
                    if event.delta.type=="thinking_delta":
                        yield event.delta.thinking
                    elif event.delta.type=="text_delta":
                        final_response+=event.delta.text
        
        final_response=json.loads(final_response)
        file_name=f'{str(uuid.uuid4())}.json'
        file_path=os.path.join("configs",file_name)
        with open(file_path,'w') as f:
            json.dump(final_response,f,indent=4)     
        
        yield json.dumps({"message": "Configuration saved", "file_path": file_path, "response": final_response}, indent=2)


    except Exception as e:
          yield json.dumps({"error": str(e)}, indent=2)

                    

            

