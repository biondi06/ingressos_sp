import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { io } from 'socket.io-client';
import './App.css'; 
import spfcLogo from './assets/spfc-logo.png';  

interface BotFormData {
  url: string;
  cpf: string;
  numberOfTickets: number;
  username: string;
  password: string;
  sectionsWithoutDiscount: string[];
}

const availableSections = [
  "ARQUIBANCADA NORTE OREO", 
  "ARQUIBANCADA SUL DIAMANTE NEGRO",
  "CADEIRA SUPERIOR NORTE OREO",
  "CADEIRA SUPERIOR SUL DIAMANTE NEGRO", 
  "CADEIRA ESPECIAL OESTE OURO BRANCO",
  "CAMAROTE CORPORATIVO SPFC",
  "ARQUIBANCADA SUL DIAMANTE NEGRO",
  "CADEIRA TÉRREA LESTE LACTA"
];

const App: React.FC = () => {
  const [formData, setFormData] = useState<BotFormData>({
    url: '',
    cpf: '',
    numberOfTickets: 1,
    username: '',
    password: '',
    sectionsWithoutDiscount: []
  });

  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<string[]>([]); 

  useEffect(() => {
    const socket = io('http://localhost:5000');  

    socket.on('status_update', (data: { message: string }) => {
      setMessages((prevMessages) => {
        const newMessages = [...prevMessages, data.message];
        if (newMessages.length > 5) {
          newMessages.shift(); 
        }
        return newMessages;
      });
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData((prevState) => {
      if (checked) {
        return {
          ...prevState,
          sectionsWithoutDiscount: [...prevState.sectionsWithoutDiscount, name],
        };
      } else {
        return {
          ...prevState,
          sectionsWithoutDiscount: prevState.sectionsWithoutDiscount.filter((section) => section !== name),
        };
      }
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/start-bot', formData);
      console.log('Response:', response);
      if (response.data.message) {
        setMessages([...messages, 'Bot iniciado com sucesso!']);
      } else {
        setMessages([...messages, 'Erro ao iniciar o bot.']);
      }
    } catch (error) {
      console.error('Erro ao enviar a requisição:', error);
      setMessages([...messages, 'Ocorreu um erro ao enviar a requisição.']);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        {}
        <img src={spfcLogo} alt="São Paulo FC" className="App-logo-left" />
        <h1>Bot - ingressos São Paulo FC</h1>
        {}
        <img src={spfcLogo} alt="São Paulo FC" className="App-logo-right" />
      </header>
      <div className="form-container">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>URL do Evento:</label>
            <input type="text" name="url" value={formData.url} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>CPF:</label>
            <input type="text" name="cpf" value={formData.cpf} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Número de Ingressos:</label>
            <input type="number" name="numberOfTickets" value={formData.numberOfTickets} onChange={handleChange} min="1" required />
          </div>
          <div className="form-group">
            <label>Usuário (Email):</label>
            <input type="text" name="username" value={formData.username} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Senha:</label>
            <input type="password" name="password" value={formData.password} onChange={handleChange} required />
          </div>

          <div className="section-selection">
            <h3>Selecione os Setores:</h3>
            <div className="sections-grid">
              {availableSections.map((section) => (
                <div className="section-card" key={section}>
                  <label>
                    <input
                      type="checkbox"
                      name={section}
                      checked={formData.sectionsWithoutDiscount.includes(section)}
                      onChange={handleCheckboxChange}
                    />
                    {section}
                  </label>
                </div>
              ))}
            </div>
          </div>

          <button type="submit" className="submit-button" disabled={isLoading}>
            {isLoading ? 'Iniciando Bot...' : 'Iniciar Bot'}
          </button>
        </form>

        {}
        <div className="status-messages">
          {messages.map((message, index) => (
            <p key={index}>{message}</p>
          ))}
        </div>
      </div>
      <footer className="App-footer">
        <p>Desenvolvido por Daniel Biondi 🎸</p>
      </footer>
    </div>
  );
};

export default App;
