import inspect
import os
from pathlib import Path
from typing import Annotated, Callable, Dict, List, TypedDict

import yaml
from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from notion_client import Client

# Load environment variables
load_dotenv()

# Initialize Notion Client
notion = Client(auth=os.getenv("NOTION_TOKEN"))


# Load system prompt from YAML file
def load_system_prompt() -> SystemMessage:
    current_dir = Path(__file__).parent
    system_prompt_path = current_dir / "system_prompt.yaml"

    try:
        with open(system_prompt_path, "r", encoding="utf-8") as file:
            yaml_content = yaml.safe_load(file)
            content = yaml_content.get("system_prompt", "")
            return SystemMessage(content=content)
    except Exception as e:
        print(f"Error loading system prompt: {str(e)}")
        return ""


class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


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
            llm, tools=self.tools, prompt=self.system_prompt
        )

    def _get_class_methods(self) -> Dict[str, Callable]:
        """Obtiene todos los métodos de la clase excepto los métodos especiales y privados"""
        methods = {}
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if not name.startswith("_"):
                methods[name] = method
        return methods

    def _create_tools(self):
        """Crea herramientas a partir de los métodos de la clase"""
        tools = []
        for name, method in self.class_methods.items():
            tools.append(tool(description=method.__doc__ or f"Tool for {name}")(method))
        return tools

    def add_block(self, *, page_id: str | None = None, blocks: List[dict]) -> str:
        """
        Agrega un bloque de contenido a una página Notion

        Args:
            blocks (List[dict]): Lista de bloques de contenido
            page_id (str | None, optional): Id de la página Notion. Defaults to None.
        """
        page_id = page_id or os.getenv("PARENT_PAGE_ID")
        return notion.blocks.children.append(block_id=page_id, children=blocks)

    def get_block(self, *, block_id: str | None = None) -> str:
        """
        Obtiene el contenido de un bloque de contenido de Notion.

        Este contenido incluye información de los hijos del bloque y sus ids.

        Args:
            block_id (str): Id del bloque de contenido de Notion

        Returns:
            str: Contenido del bloque de contenido
        """
        block_id = block_id or os.getenv("PARENT_PAGE_ID")
        return notion.blocks.children.list(block_id=block_id)

    def create_page(
        self,
        *,
        page_id: str | None = None,
        title: str,
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
                    "parent": {
                        "type": "page_id",
                        "page_id": page_id or os.getenv("PARENT_PAGE_ID"),
                    },
                    "properties": {
                        "title": [{"type": "text", "text": {"content": title}}]
                    },
                }
            )

            return f"Page created successfully: {page['id']}"
        except Exception as e:
            return f"Error creating page: {str(e)}"

    def create_database(
        self,
        *,
        page_id: str | None = None,
        title: str,
        properties: dict,
    ) -> str:
        """Create a new Notion database with the specified title and optional custom properties

        Args:
        page_id (str | None, optional): The id of the page where the new database will be created as a child.
            If not provided, the new database will be created as a child of the
            page with id provided by the env variable PARENT_PAGE_ID.
        title (str): The title of the new database
        properties (dict): A dictionary of custom properties to be added to the database
        """
        try:
            database = notion.databases.create(
                **{
                    "parent": {
                        "type": "page_id",
                        "page_id": page_id or os.getenv("PARENT_PAGE_ID"),
                    },
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": title, "link": None},
                        }
                    ],
                    "properties": properties,
                }
            )

            return f"Database created successfully: {database['id']}"
        except Exception as e:
            return f"Error creating database: {str(e)}"

    def invoke(self, prompt: str) -> str:
        """Invoca el agente con un prompt y devuelve la respuesta"""

        result = self.compiled_agent.invoke(
            {"messages": [HumanMessage(content=prompt)]}, {"recursion_limit": 25}
        )
        # Extraer el contenido del último mensaje
        return result["messages"][-1].content


# Example usage
if __name__ == "__main__":
    agent = NotionAgent()
    print(agent.invoke("Dame información sobre todas las páginas disponibles"))
