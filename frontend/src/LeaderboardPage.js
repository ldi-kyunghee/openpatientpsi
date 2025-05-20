import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LeaderboardPage.css';

function LeaderboardPage() {
  const [sortedModels, setSortedModels] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://localhost:8000/leaderboard")
      .then(res => res.json())
      .then(data => {
        const filtered = Object.entries(data)
          .filter(([key]) => key !== "Tie" && key !== "Both Bad")
          .sort((a, b) => b[1] - a[1]);
        setSortedModels(filtered);
      })
      .catch(err => console.error("리더보드 로딩 실패", err));
  }, []);

  return (
    <div className="leaderboard-container">
      <h1 className="leaderboard-title">🏆 리더보드</h1>
      <button className="back-button" onClick={() => navigate("/")}>
        ← 돌아가기
      </button>

      <div className="leaderboard-list">
        {sortedModels.map(([model, votes], index) => (
          <div className="leaderboard-card" key={model}>
            <div className="model-info">
              <span className="rank">{index + 1}</span>
              <span className="model-name">
                {model === "openpsi"
                  ? "OpenPSI 0.5B"
                  : model === "gpt4o"
                  ? "GPT-4.1 nano"
                  : model}
              </span>
            </div>
            <div className="vote-count">{votes}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default LeaderboardPage;
