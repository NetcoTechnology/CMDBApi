# CMDBApiWrapper

## Installation

```bash
mkdir myproject
cd myproject
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install git+https://github.com/NetcoTechnology/CMDBApiWrapper python-dotenv
```

## Usage
setup .env file with the following variables
```
USERNAME=<myusername>
PASSWORD=<mypassword>
BASE_URL=https://<myfqdn>/cmdbuild/services/rest/v3/  
```
  
you can use the api wrapper as follows  
```python
from cmdbapipy import CMDBApi
import os
from dotenv import load_dotenv

# example uses python-dotenv to load .env into environment
load_dotenv()

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
base_url = os.getenv("BASE_URL")

api = CMDBApi(
    username=username,
    password=password,
    base_url=base_url,
    debug=True
)

# make an api call, any http verb is supported and all extra parms will be submitted as json data
result = api.get("classes")
```

# Filtering
```python
api.get("classes/Internet/cards", params={"filter": '{"query":"Y2011238244"}'})
```

filter specific fields  
```python
api.get("classes/Internet/cards",params={"filter": '{"attribute":{"and":[{"simple":{"attribute":"Code","operator":"equal","parameterType":"fixed","value":["Y2011238244"],"category":null,"model":null}}]}}'})
```


# Creating new objects in cmdb (example)
```python
import os
from dotenv import load_dotenv
from cmdbapipy import CMDBApi
from pprint import pprint

# The following line installs the necessary package to manage environment variables:
# pip install python-dotenv

# Load environment variables from a .env file:
load_dotenv()

# Retrieve API credentials and the base URL from environment variables:
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
base_url = os.getenv("BASE_URL")


# Initialize the CMDB API with the fetched credentials and base URL, enabling debug mode for verbose output:
api = CMDBApi(
    username=username,
    password=password,
    base_url=base_url,
    debug=True
)

def create_internet_card(partner, description):
    """
    Creates an internet service card in the CMDB for a specified partner with a given description.

    Args:
    partner (str): Name of the partner for whom the internet card is being created.
    description (str): Description of the internet service.

    Returns:
    str or None: Returns the code of the created internet card if successful, None otherwise.
    """

    # Fetch existing partners from the CMDB and create a dictionary mapping descriptions to IDs:
    partners = {x['Description']: x['_id'] for x in api.get("classes/Partner/cards")['data']}
    # Check if the partner exists in the fetched list:
    if partner in partners:
        # Post a new internet card with specified details and default values:
        result = api.post("classes/Internet/cards",
	        json={
	            "Code": None,
	            "Description": description,
	            "OpsState": api.lookup_types("OpsStatus")['Planned'],
	            "Partner": partners[partner],
	            "RIPEHandle": None,
	            "CustRef": None,
	            "SVCDesign": None,
	            "SVCDrawing": None,
	            "Notes": "mynote"
	        } 
        )
        return result['data']['Code']
    else:
        return None

code = create_internet_card(partner="Netco Technology B.V.", description="test internet card")
print(code)
```

# Tips
The CMDB frontend uses the same API as this wrapper, it can be helpfull to analyze how the frontend utilizes this API using the network tab in your browser debugging tools. 

---

## CMDBApi class

This Python class provides an interface to interact with the CMDBuild REST API. It manages session authentication, API requests, and logging, with support for any HTTP method through attribute-based dynamic dispatch.

### Constructor

#### `__init__(self, username: str, password: str, timeout: Optional[int] = 30, debug: bool = False, base_url: str)`

Initializes a new instance of the CMDBApi class.

- **Parameters:**
  - `username` (str): The username for authentication.
  - `password` (str): The password for authentication.
  - `verify` (Optional[bool]): Certificate verification. Defaults to True.
  - `timeout` (Optional[int]): The timeout for API requests. Defaults to 30 seconds.
  - `debug` (bool): If set to `True`, enables detailed HTTP request and response logging.
  - `base_url` (str): The base URL for the CMDBuild REST API. Defaults to the provided URL.

### Methods

#### `__getattr__(self, attr)`

Allows dynamic dispatch of HTTP methods via attribute access, which simplifies calling API methods directly as `api.get(...)`, `api.post(...)`, etc.

- **Parameters:**
  - `attr` (str): The HTTP method to use for the request.
- **Returns:**
  - A partial function that completes the `api_request` method call, configured to use the HTTP method as the name of the attribute accessed.

#### `api_request(self, endpoint: str, method: str = "get", timeout: Optional[int] = None, params: Optional[dict] = None, **kwargs) -> Any`

Makes a generic API request to a specified endpoint using a dynamic HTTP method.

- **Parameters:**
  - `endpoint` (str): The API endpoint to request.
  - `method` (str): The HTTP method to use, dynamically resolved based on method attribute access.
  - `timeout` (Optional[int]): Custom timeout for this request, defaults to the class timeout.
  - `params` (Optional[dict]): URL parameters to include in the request.
  - `**kwargs`: Additional keyword arguments, usually passed as JSON payload.
- **Returns:**
  - The JSON data from the API response if successful; otherwise, it handles and logs errors.

#### `lookup_types(self, name: str) -> dict`

Converts a name to its hexadecimal representation and fetches corresponding types from the CMDB.

- **Parameters:**
  - `name` (str): The name to look up.
- **Returns:**
  - A dictionary mapping descriptions to their respective IDs in the CMDB.



