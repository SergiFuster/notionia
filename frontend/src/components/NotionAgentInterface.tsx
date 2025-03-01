import React, { useState } from 'react';
import axios, { AxiosError } from 'axios';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import remarkGfm from 'remark-gfm';
import './NotionAgentInterface.css';

export const NotionAgentInterface: React.FC = () => {
  const [prompt, setPrompt] = useState<string>('');
  const [response, setResponse] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [conversation, setConversation] = useState<Array<{type: 'user' | 'agent', text: string}>>([]);
  const [debugInfo, setDebugInfo] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!prompt.trim()) return;
    
    // Add user message to conversation
    setConversation(prev => [...prev, { type: 'user', text: prompt }]);
    setDebugInfo('');
    
    setIsLoading(true);
    
    try {
      console.log('Enviando solicitud al backend:', prompt);
      
      // Call the backend API
      const response = await axios.post('http://127.0.0.1:8000/api/agent/invoke', {
        prompt
      });
      
      console.log('Respuesta recibida del backend:', response.data);
      
      // Add agent response to conversation
      setConversation(prev => [...prev, { type: 'agent', text: response.data.response }]);
      setResponse(response.data.response);
    } catch (error) {
      console.error('Error invoking agent:', error);
      // Mostrar el mensaje de error específico si está disponible
      let errorMessage = 'Lo siento, ocurrió un error al procesar tu solicitud. Por favor, intenta de nuevo.';
      let debugDetails = '';
      
      // Verificar si el error es una instancia de AxiosError
      if (axios.isAxiosError(error)) {
        // Ahora TypeScript sabe que error es un AxiosError
        const axiosError = error as AxiosError<any>;
        debugDetails = `Status: ${axiosError.response?.status || 'N/A'}, 
                        Data: ${JSON.stringify(axiosError.response?.data || {})}, 
                        Message: ${axiosError.message}`;
        
        if (axiosError.response?.data?.detail) {
          errorMessage = axiosError.response.data.detail;
        }
      } else if (error instanceof Error) {
        debugDetails = `Error: ${error.message}, Stack: ${error.stack}`;
      } else {
        debugDetails = `Error desconocido: ${String(error)}`;
      }
      
      console.log('Detalles del error:', debugDetails);
      setDebugInfo(debugDetails);
      
      setConversation(prev => [...prev, { 
        type: 'agent', 
        text: errorMessage
      }]);
    } finally {
      setIsLoading(false);
      setPrompt('');
    }
  };

  // Componente para renderizar mensajes con soporte para Markdown
  const MessageContent = ({ text, type }: { text: string, type: 'user' | 'agent' }) => {
    if (type === 'user') {
      // Los mensajes del usuario se muestran como texto plano
      return <p>{text}</p>;
    } else {
      // Los mensajes del agente se renderizan como Markdown con resaltado de sintaxis
      return (
        <div className="markdown-content">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code: ({ node, inline, className, children, ...props }: any) => {
                const match = /language-(\w+)/.exec(className || '');
                return !inline && match ? (
                  <SyntaxHighlighter
                    language={match[1]}
                    PreTag="div"
                    {...props as any}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              },
              a: ({ node, ...props }: any) => (
                <a
                  {...props}
                  target="_blank"
                  rel="noopener noreferrer"
                />
              )
            }}
          >
            {text}
          </ReactMarkdown>
        </div>
      );
    }
  };

  return (
    <div className="notion-agent-interface">
      <div className="conversation-container">
        {conversation.length === 0 ? (
          <div className="empty-conversation">
            <p>Envía un mensaje para comenzar a interactuar con el agente de Notion.</p>
          </div>
        ) : (
          conversation.map((message, index) => (
            <div key={index} className={`message ${message.type}`}>
              <div className="message-content">
                <MessageContent text={message.text} type={message.type} />
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message agent loading">
            <div className="loading-indicator">
              <div></div>
              <div></div>
              <div></div>
            </div>
          </div>
        )}
        
        {debugInfo && (
          <div className="debug-info">
            <h4>Información de depuración:</h4>
            <pre>{debugInfo}</pre>
          </div>
        )}
      </div>
      
      <form onSubmit={handleSubmit} className="prompt-form">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Escribe tu mensaje aquí..."
          rows={3}
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !prompt.trim()}>
          {isLoading ? 'Enviando...' : 'Enviar'}
        </button>
      </form>
    </div>
  );
};
