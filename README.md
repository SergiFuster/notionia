# Notionia

Notionia es una aplicación que te permite interactuar con un agente de Notion para gestionar tu espacio de trabajo de manera eficiente.

## Estructura del Proyecto

```
notionia/
├── backend/
│   ├── src/
│   │   ├── agent/
│   │   │   ├── notion_agent.py
│   │   │   └── system_prompt.yaml
│   │   └── api/
│   │       └── app.py
│   ├── .env
│   └── pyproject.toml
└── frontend/
    ├── public/
    │   └── index.html
    ├── src/
    │   ├── components/
    │   │   ├── NotionAgentInterface.tsx
    │   │   └── NotionAgentInterface.css
    │   ├── App.tsx
    │   ├── App.css
    │   ├── index.tsx
    │   └── index.css
    ├── package.json
    └── tsconfig.json
```

## Requisitos

- Python 3.11+
- Node.js 14+
- npm 6+

## Configuración

### Backend

1. Crea un archivo `.env` en la carpeta `backend` con las siguientes variables:

```
NOTION_TOKEN=tu_token_de_notion
PARENT_PAGE_ID=id_de_pagina_padre
OPENAI_API_KEY=tu_api_key_de_openai
```

2. Instala las dependencias:

```bash
cd backend
pip install -e .
```

3. Ejecuta el servidor:

```bash
cd backend/src/api
uvicorn app:app --reload --port 5000
```

### Frontend

1. Instala las dependencias:

```bash
cd frontend
npm install
```

2. Ejecuta el servidor de desarrollo:

```bash
npm start
```

## Uso

1. Abre tu navegador en `http://localhost:3000` para acceder a la interfaz de usuario
2. Escribe un mensaje para interactuar con el agente de Notion
3. El agente responderá a tus solicitudes y realizará acciones en tu espacio de trabajo de Notion
4. Para explorar la API directamente, visita `http://localhost:5000/docs` para ver la documentación interactiva de Swagger

## Características

- Crear nuevas páginas con contenido formateado
- Crear nuevas bases de datos con propiedades personalizadas
- Actualizar páginas existentes con nuevo contenido
- Interfaz de usuario intuitiva para interactuar con el agente
- API RESTful con documentación interactiva
