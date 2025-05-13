import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function LeaderboardPage() {
  const [leaderboard, setLeaderboard] = useState({
    vllm: 0,
    chatgpt: 0,
    Tie: 0,
    'Both Bad': 0
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://localhost:8001/leaderboard")
      .then(res => res.json())
      .then(data => setLeaderboard(data))
      .catch(err => console.error("리더보드 로딩 실패", err));
  }, []);

  return (
    <div className="App">
      <h1>🏆 리더보드</h1>
      <button onClick={() => navigate("/")}>← 돌아가기</button>
      <table>
        <thead>
          <tr>
            <th>항목</th>
            <th>득표 수</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>beomi/KoAlpaca-Polyglot-13B</td>
            <td>{leaderboard.vllm ?? 0}</td>
          </tr>
          <tr>
            <td>gpt-3.5-turbo</td>
            <td>{leaderboard.chatgpt ?? 0}</td>
          </tr>
          <tr>
            <td>Tie</td>
            <td>{leaderboard.Tie ?? 0}</td>
          </tr>
          <tr>
            <td>Both Bad</td>
            <td>{leaderboard["Both Bad"] ?? 0}</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export default LeaderboardPage;
