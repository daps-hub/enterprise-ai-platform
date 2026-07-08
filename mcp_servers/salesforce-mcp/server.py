from simple_salesforce import Salesforce
from dotenv import load_dotenv
import os

from mcp.server.fastmcp import FastMCP
load_dotenv()

mcp = FastMCP("salesforce-mcp-server")

def get_salesforce():
    return Salesforce(
        username=os.getenv("SALESFORCE_USERNAME"),
        password=os.getenv("SALESFORCE_PASSWORD"),
        security_token=os.getenv("SALESFORCE_SECURITY_TOKEN"),
        domain=os.getenv("SALESFORCE_DOMAIN", "login"),
    )
    
@mcp.tool()
def search_accounts(account_name: str):
    """Search for accounts in Salesforce by name."""
    sf = get_salesforce()
    safe_name = account_name.replace("'", "\\'") 
    query = f"SELECT Id, Name FROM Account WHERE Name LIKE '%{safe_name}%' LIMIT 10"
    #query = f"SELECT Id, Name FROM Account WHERE Name LIKE '%{account_name}%'"
    result = sf.query(query)
    return result['records']

@mcp.tool()
def get_account(account_id: str):
    """Get account details from Salesforce by ID."""
    sf = get_salesforce()
    account = sf.Account.get(account_id)
    return account

@mcp.tool()
def search_contacts(contact_name: str):
    """Search for contacts in Salesforce by name."""
    sf = get_salesforce()
    query = f"SELECT Id, FirstName, LastName, Email FROM Contact WHERE FirstName LIKE '%{contact_name}%' OR LastName LIKE '%{contact_name}%'"
    result = sf.query(query)
    return result['records']
@mcp.tool()
def search_opportunities(opportunity_name: str):
    """Search for opportunities in Salesforce by name."""
    sf = get_salesforce()
    query = f"SELECT Id, Name, StageName, CloseDate FROM Opportunity WHERE Name LIKE '%{opportunity_name}%'"
    result = sf.query(query)
    return result['records']

@mcp.tool()
def list_open_opportunities():
    """List all open opportunities in Salesforce."""
    sf = get_salesforce()
    query = "SELECT Id, Name, StageName, CloseDate FROM Opportunity WHERE IsClosed = FALSE"
    result = sf.query(query)
    return result['records']

if __name__ == "__main__":
    mcp.run(transport="stdio")