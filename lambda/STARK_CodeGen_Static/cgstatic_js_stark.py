#STARK Code Generator component.
#Produces the customized static content for a STARK system

#Python Standard Library
import textwrap

#Private modules
import convert_friendly_to_system as converter

def create(data):

    api_gateway_id  = data['API Gateway ID']
    entities        = data['Entities']

    source_code = f"""\
        const STARK={{
            'sys_modules_url':'https://{api_gateway_id}.execute-api.ap-southeast-1.amazonaws.com/sys_modules',"""

    #Each entity is a big module, has own endpoint
    for entity in entities:
        entity_endpoint_name = converter.convert_to_system_name(entity)
        source_code += f"""
            '{entity_endpoint_name}_url':'https://{api_gateway_id}.execute-api.ap-southeast-1.amazonaws.com/{entity_endpoint_name}',"""

    #STARK-provided common methods go here
    source_code += f"""
            'methods_with_body': ["POST", "DELETE", "PUT"],

            request: function(method, fetchURL, payload='') {{

                let fetchData = {{
                    mode: 'cors',
                    headers: {{ "Content-Type": "application/json" }},
                    method: method,
                }}

                if(this.methods_with_body.includes(method)) {{
                    console.log("stringifying payload")
                    console.log(payload)
                    fetchData['body'] = JSON.stringify(payload)
                }}

                return fetch(fetchUrl, fetchData).then( function(response) {{
                    if (!response.ok) {{
                        console.log(response)
                        throw Error(response.statusText);
                    }}
                    return response
                }}).then((response) => response.json())
            }}
        }};
    """

    return textwrap.dedent(source_code)