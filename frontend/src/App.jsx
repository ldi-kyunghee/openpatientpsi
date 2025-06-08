import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import LeaderboardPage from './LeaderboardPage';
import './App.css';

const patients = [
  { id: -1, name: "환자 없음" },
  { id: 0, name: "환자 1" },
  { id: 1, name: "환자 2" },
  { id: 2, name: "환자 3" },
  { id: 3, name: "환자 4" },
  { id: 4, name: "환자 5" },
  { id: 5, name: "환자 6" },
  { id: 6, name: "환자 7" },
  { id: 7, name: "환자 8" },
  { id: 8, name: "환자 9" },
  { id: 9, name: "환자 10" },
];

function App() {
  const [message, setMessage] = useState('');
  const [isAutoMessage, setIsAutoMessage] = useState(false);
  const [response, setResponse] = useState({ openpsi: '', gpt4o: '' });
  const [submittedMessage, setSubmittedMessage] = useState('');
  const [vote, setVote] = useState(null);
  const [showModelNames, setShowModelNames] = useState(false);
  const [selectedPatientId, setSelectedPatientId] = useState(-1);
  const [modelOrder, setModelOrder] = useState(["openpsi", "gpt4o"]);
  const [showPromptModal, setShowPromptModal] = useState(false);
  const [customPatientData, setCustomPatientData] = useState({
    relevant_history: '',
    core_beliefs: '',
    intermediate_beliefs: '',
    intermediate_depression: '',
    coping_strategies: '',
    situation: '',
    automatic_thoughts: '',
    emotions: '',
    behaviors: '',
    conversational_styles: '',
});

const navigate = useNavigate();


  const defaultPrompt = `
- 환자의 현재 상황을 고려하여 적절한 질문을 입력해주세요.

    Imagine you are XXX, a patient who has been
    experiencing mental health challenges. You have
    been attending therapy sessions for several weeks.
    Your task is to engage in a conversation with
    the therapist as XXX would during a cognitive
    behavioral therapy (CBT) session. Align your
    responses with XXX’s background information
    provided in the ‘Relevant history’ section. Your
    thought process should be guided by the cognitive
    conceptualization diagram in the ‘Cognitive
    Conceptualization Diagram’ section, but avoid
    directly referencing the diagram as a real patient
    would not explicitly think in those terms.

    Patient History: {history}

    Cognitive Conceptualization Diagram:
    Core Beliefs: {core_beliefs}
    Intermediate Beliefs: {intermediate_beliefs}
    Intermediate Beliefs during Depression: {intermediate_depression}
    Coping Strategies: {coping_strategies}

    You will be asked about your experiences
    over the past week. Engage in a conversation with
    the therapist regarding the following situation
    and behavior. Use the provided emotions and
    automatic thoughts as a reference, but do not
    disclose the cognitive conceptualization diagram
    directly. Instead, allow your responses to be
    informed by the diagram, enabling the therapist
    to infer your thought processes.

    Situation: {situation}
    Automatic thoughts: {automatic_thoughts}
    Emotions: {emotions}
    Behaviors: {behaviors}

    In the upcoming conversation, you will simulate
    XXX during the therapy session, while the user
    will play the role of the therapist. Adhere
    to the following guidelines:
    {style_description}
    2. Emulate the demeanor and responses of a genuine patient
    to ensure authenticity in your interactions. Use
    natural language, including hesitations, pauses,
    and emotional expressions, to enhance the realism
    of your responses.
    3. Gradually reveal deeper concerns and core issues, as a real patient often
    requires extensive dialogue before delving into
    more sensitive topics. This gradual revelation
    creates challenges for therapists in identifying
    the patient’s true thoughts and emotions.
    4. Maintain consistency with XXX’s profile
    throughout the conversation. Ensure that your
    responses align with the provided background
    information, cognitive conceptualization diagram,
    and the specific situation, thoughts, emotions,
    and behaviors described.
    5. Engage in a dynamic
    and interactive conversation with the therapist.
    Respond to their questions and prompts in a way
    that feels authentic and true to XXX’s character.
    Allow the conversation to flow naturally, and avoid
    providing abrupt or disconnected responses.

    You are now XXX. Respond to the therapist’s prompts
    as XXX would, regardless of the specific questions
    asked. Limit each of your responses to a maximum
    of 5 sentences.
`;

  useEffect(() => {
    const fetchAutoMessage = async () => {
      if (selectedPatientId !== -1) {
        const selectedPatient = patients.find(p => p.id === selectedPatientId);
        if (selectedPatient) {
          const autoMessage = selectedPatient.name;
          setMessage(autoMessage);
          setIsAutoMessage(true);

          const shuffled = Math.random() < 0.5 ? ["openpsi", "gpt4o"] : ["gpt4o", "openpsi"];
          setModelOrder(shuffled);
          setSubmittedMessage(autoMessage);
          setVote(null);
          setShowModelNames(false);
          setResponse({ openpsi: '응답 대기 중...', gpt4o: '응답 대기 중...' });

          try {
            const res = await fetch('http://localhost:8000/compare', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                message: autoMessage,
                model_order: shuffled,
                patient_id: selectedPatientId
              })
            });

            const data = await res.json();
            setResponse(data);
          } catch (error) {
            setResponse({
              openpsi: '[에러] 응답을 가져오지 못했습니다.',
              gpt4o: '[에러] 응답을 가져오지 못했습니다.'
            });
          }
        }
      } else {
        setMessage('');
        setIsAutoMessage(false);
      }
    };

    fetchAutoMessage();
  }, [selectedPatientId]);

  const handleSubmit = async () => {
    if (selectedPatientId !== -1 && !message.trim()) return;

    if (selectedPatientId === -1) {
      for (const [key, value] of Object.entries(customPatientData)) {
        if (!value.trim()) {
          alert(`"${key.replace(/_/g, ' ')}" 항목을 입력해주세요.`);
          return;
        }
      }
    }

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
        body: JSON.stringify({
          message,
          model_order: shuffled,
          patient_id: selectedPatientId,
          ...(selectedPatientId === -1 ? { custom_patient_data: customPatientData } : {})
        })
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

      <div className="dropdown-section">
        <label htmlFor="patient-select">🧍 환자 선택: </label>
        <select
          id="patient-select"
          value={selectedPatientId}
          onChange={(e) => setSelectedPatientId(Number(e.target.value))}
        >
          {patients.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
      </div>

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

      {selectedPatientId === -1 && (
        <div className="custom-patient-form">
          <h3>📝 사용자 정의 환자 프로필 입력</h3>

          <button
            type="button"
            onClick={() => setShowPromptModal(true)}
            style={{ marginBottom: '12px' }}
          >
            📄 기본 프롬프트 보기
          </button>

          <div className="custom-patient-grid">
            {Object.keys(customPatientData).map((key) => (
              <div key={key} className="form-group">
                <label>{key.replace(/_/g, ' ')}:</label>
                <input
                  type="text"
                  value={customPatientData[key]}
                  placeholder={`${key.replace(/_/g, ' ')} 입력해주세요`}
                  onChange={(e) =>
                    setCustomPatientData({ ...customPatientData, [key]: e.target.value })
                  }
                />
              </div>
            ))}
          </div>
          <button onClick={handleSubmit} style={{ marginTop: '12px' }}>질문하기</button>
        </div>
      )}

      <div className="vote-buttons">
        <button onClick={() => handleVote('A is better')}>👍 A is better</button>
        <button onClick={() => handleVote('B is better')}>👍 B is better</button>
        <button onClick={() => handleVote('Tie')}>⚖️ Tie</button>
        <button onClick={() => handleVote('Both are bad')}>👎 Both are bad</button>
      </div>

      <button onClick={() => navigate("/leaderboard")}>🏆 리더보드 보기</button>

      {/* Modal 영역 추가 */}
      {showPromptModal && (
        <div className="modal-backdrop" onClick={() => setShowPromptModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>📄 기본 프롬프트</h3>
            <pre style={{ whiteSpace: 'pre-wrap', padding: '12px', backgroundColor: '#f5f5f5', borderRadius: '6px', maxHeight: '400px', overflowY: 'auto' }}>
              {defaultPrompt}
            </pre>
            <button onClick={() => setShowPromptModal(false)} style={{ marginTop: '12px' }}>닫기</button>
          </div>
        </div>
      )}
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
