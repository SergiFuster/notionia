import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from notion_client import Client
from typing import TypedDict, Annotated, List, Dict, Callable
import inspect
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent

# Load environment variables
load_dotenv()

# Initialize Notion Client
notion = Client(auth=os.getenv("NOTION_TOKEN"))

# Load system prompt from YAML file
def load_system_prompt() -> SystemMessage:
    current_dir = Path(__file__).parent
    system_prompt_path = current_dir / "system_prompt.yaml"
    
    try:
        with open(system_prompt_path, 'r', encoding='utf-8') as file:
            yaml_content = yaml.safe_load(file)
            content = yaml_content.get("system_prompt", "")
            return SystemMessage(content=content)
    except Exception as e:
        print(f"Error loading system prompt: {str(e)}")
        return ""

class AgentState(TypedDict):
    messages : Annotated[List[AnyMessage], add_messages]
    
class NotionAgent:
    def __init__(self, llm=ChatOpenAI(model="gpt-4o")):
        self.llm = llm
        # Cargar el system prompt
        self.system_prompt = load_system_prompt()
        # Guardar todas las funciones de la clase en una propiedad
        self.class_methods = self._get_class_methods()
        # Crear herramientas a partir de los métodos de la clase
        self.tools = self._create_tools()
        # Crear el agente ReAct con el system prompt
        self.compiled_agent = create_react_agent(
            llm, 
            tools=self.tools,
            prompt=self.system_prompt
        )
    
    def _get_class_methods(self) -> Dict[str, Callable]:
        """Obtiene todos los métodos de la clase excepto los métodos especiales y privados"""
        methods = {}
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            # Excluir métodos especiales (como __init__) y métodos privados (que comienzan con _)
            if not name.startswith('_'):
                methods[name] = method
        return methods
    
    def _create_tools(self):
        """Crea herramientas a partir de los métodos de la clase"""
        tools = []
        for name, method in self.class_methods.items():
            tools.append(tool(description=method.__doc__ or f"Tool for {name}")(method))
        return tools
    def add_content_block_to_page(self, page_id: str, content: dict):
        notion.blocks.children.append(
            block_id=page_id,
            **content
        )
    def create_page(
        self,
        *,
        page_id : str | None = None,
        title : str,
        description : str,
        ) -> str:
        """
        Create a new Notion page with the specified parent and title

        Args:
        page_id: str | None, optional
            The id of the page where the new page will be created as a child.
            If not provided, the new page will be created as a child of the
            page with id provided by the env variable PARENT_PAGE_ID.
        title: str
            The title of the new page
        
        """
        try:            
            # Crear la página
            page = notion.pages.create(
                **{
                    "parent" : {"type": "page_id", "page_id": page_id or os.getenv("PARENT_PAGE_ID")},
                    "properties" : {
                        "title": [
                            {
                                "type": "text",
                                "text": {
                                    "content": title
                                }
                            }
                        ]
                    }
                }
            )
            
            return f"Page created successfully: {page['id']}"
        except Exception as e:
            return f"Error creating page: {str(e)}"
    
    def create_database(self, title: str, properties: dict = None) -> str:
        """Create a new Notion database with the specified title and optional custom properties"""
        try:
            # Propiedades por defecto si no se proporcionan
            default_properties = {
                "Name": {"title": {}},
                "Description": {"rich_text": {}}
            }
            
            # Usar propiedades personalizadas si se proporcionan
            db_properties = properties if properties else default_properties
            
            database = notion.databases.create(
                parent={"type": "page_id", "page_id": os.getenv("PARENT_PAGE_ID")},
                title=[{"type": "text", "text": {"content": title}}],
                properties=db_properties
            )
            return f"Database created successfully: {database['id']}"
        except Exception as e:
            return f"Error creating database: {str(e)}"
    
    def get_page(self, page_id: str = os.getenv("PARENT_PAGE_ID")) -> str:
        """Get information about a specific Notion page

        Args:
            page_id: str, optional
                The id of the page to retrieve. Defaults to the page with id provided by the env variable PARENT_PAGE_ID.
        """
        try:
            page = notion.pages.retrieve(page_id=page_id)
            return page
        except Exception as e:
            return f"Error retrieving page: {str(e)}"
    
    def invoke(self, prompt: str) -> str:
        """Invoca el agente con un prompt y devuelve la respuesta"""
        
        result = self.compiled_agent.invoke({"messages": [HumanMessage(content=prompt)]}, {"recursion_limit" : 25})
        # Extraer el contenido del último mensaje
        return result["messages"][-1].content
    
# Example usage
if __name__ == "__main__":
    agent = NotionAgent()
    print(agent.invoke("Dame información sobre todas las páginas disponibles"))
