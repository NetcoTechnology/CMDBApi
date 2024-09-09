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
    verify=False,
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
