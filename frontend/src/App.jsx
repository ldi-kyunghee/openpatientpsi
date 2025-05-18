import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import LeaderboardPage from './LeaderboardPage';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState({ openpsi: '', gpt4o: '' });
  const [submittedMessage, setSubmittedMessage] = useState('');
  const [vote, setVote] = useState(null);
  const [showModelNames, setShowModelNames] = useState(false);
  const navigate = useNavigate();
  const [modelOrder, setModelOrder] = useState(["openpsi", "gpt4o"]);

  const handleSubmit = async () => {
    if (!message.trim()) return;

    const shuffled = Math.random() < 0.5 ? ["openpsi", "gpt4o"] : ["gpt4o", "openpsi"];
    setModelOrder(shuffled);

    setSubmittedMessage(message);
    setVote(null);
    setShowModelNames(false);
    setResponse({ openpsi: '응답 대기 중...', gpt4o: '응답 대기 중...' });

    try {
      const res = await fetch('http://localhost:8000/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, model_order: shuffled })
      });

      const data = await res.json();
      setResponse(data);
    } catch (error) {
      setResponse({
        openpsi: '[에러] 응답을 가져오지 못했습니다.',
        gpt4o: '[에러] 응답을 가져오지 못했습니다.'
      });
    }
  };

  const handleVote = async (option) => {
    setVote(option);
    setShowModelNames(true);
    alert(`투표 완료: ${option}`);

    try {
      await fetch('http://localhost:8000/vote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_order: modelOrder, vote: option })
      });
    } catch (error) {
      console.error('투표 전송 실패', error);
    }
  };

  const displayName = (key) => {
    if (key === "openpsi") return "OpenPSI 0.5B";
    if (key === "gpt4o") return "GPT-4o";
    return key;
  };

  return (
    <div className="App">
      <h1>🧠 LLM Battle</h1>

      <div className="battle-section">
        <div className="model-box">
          <h2>{showModelNames ? displayName(modelOrder[0]) : "Model A"}</h2>
          <div className="question-box">{submittedMessage}</div>
          <div className="answer-box">{response[modelOrder[0]]}</div>
        </div>
        <div className="model-box">
          <h2>{showModelNames ? displayName(modelOrder[1]) : "Model B"}</h2>
          <div className="question-box">{submittedMessage}</div>
          <div className="answer-box">{response[modelOrder[1]]}</div>
        </div>
      </div>

      <div className="input-section">
        <textarea
          placeholder="비교하고 싶은 질문을 입력하세요"
          value={message}
          onChange={e => setMessage(e.target.value)}
        />
        <button onClick={handleSubmit}>질문하기</button>
      </div>

      <div className="vote-buttons">
        <button onClick={() => handleVote('A is better')}>👍 A is better</button>
        <button onClick={() => handleVote('B is better')}>👍 B is better</button>
        <button onClick={() => handleVote('Tie')}>⚖️ Tie</button>
        <button onClick={() => handleVote('Both are bad')}>👎 Both are bad</button>
      </div>

      <button onClick={() => navigate("/leaderboard")}>🏆 리더보드 보기</button>
    </div>
  );
}

function RootApp() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/leaderboard" element={<LeaderboardPage />} />
      </Routes>
    </Router>
  );
}

export default RootApp;
