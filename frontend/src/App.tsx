import React, { useState } from 'react';
import './App.css';
import { NotionAgentInterface } from './components/NotionAgentInterface';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Notionia</h1>
        <p>Tu asistente para Notion</p>
      </header>
      <main>
        <NotionAgentInterface />
      </main>
      <footer>
        <p>&copy; {new Date().getFullYear()} Notionia</p>
      </footer>
    </div>
  );
}

export default App;
