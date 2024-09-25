import React, { useState } from 'react';
import axios from 'axios';
import './App.css';  // Arquivo de estilos atualizado

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
  "CAMAROTE CORPORATIVO SPFC"
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
  const [message, setMessage] = useState('');

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
    setMessage('');

    try {
      // Enviando os dados para o backend
      const response = await axios.post('http://localhost:5000/start-bot', formData);
      console.log('Response:', response);  // Log de depuração
      if (response.data.message) {
        setMessage('Bot iniciado com sucesso!');
      } else {
        setMessage('Erro ao iniciar o bot.');
      }
    } catch (error) {
      console.error('Erro ao enviar a requisição:', error);  // Log de erro
      setMessage('Ocorreu um erro ao enviar a requisição.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Ingressos São Paulo FC</h1>
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
        {message && <p className="message">{message}</p>}
      </div>
      <footer className="App-footer">
        <p>© 2024 São Paulo Futebol Clube</p>
      </footer>
    </div>
  );
};

export default App;
