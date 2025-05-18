import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

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
    <div className="App">
      <h1>🏆 리더보드</h1>
      <button onClick={() => navigate("/")}>← 돌아가기</button>
      <table>
        <thead>
          <tr>
            <th>순위</th>
            <th>모델</th>
            <th>득표 수</th>
          </tr>
        </thead>
        <tbody>
          {sortedModels.map(([model, votes], index) => (
            <tr key={model}>
              <td>{index + 1}</td>
              <td>
                {model === "openpsi" ? "OpenPSI 0.5B" :
                 model === "gpt4o" ? "GPT-4o" :
                 model}
              </td>
              <td>{votes}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default LeaderboardPage;
