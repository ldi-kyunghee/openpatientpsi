# OpenPatientPSI

OpenPatientPSI는 환자 시뮬레이션 및 LLM(대형 언어 모델) 비교를 위한 웹 애플리케이션입니다. 프론트엔드는 React 기반, 백엔드는 FastAPI 기반으로 구성되어 있습니다.

---

## 1. 백엔드

### 기술 스택

- Python 3.x
- FastAPI (비동기 REST API 서버)
- Uvicorn (ASGI 서버)
- python-dotenv (환경 변수)
- httpx, peft 등

### 주요 구조

- `main.py`: FastAPI 앱, API 라우터, CORS, 리더보드, 모델 비교 등
- `models/registry.py`: 다양한 모델 등록/관리
- `patient_example.json`: 샘플 환자 데이터
- `.env`: 환경 변수 파일

### API 주요 엔드포인트

- `POST /compare`: 두 모델의 응답 비교
- `POST /vote`: 모델 응답에 대한 투표 기록
- `GET /leaderboard`: 모델별 투표 리더보드 제공

### 실행 방법

1. 의존성 설치  
   ```
   pip install -r requirements.txt
   ```

2. 서버 실행  
   ```
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. 환경 변수 설정  
   `.env` 파일에 필요한 값을 입력

- 프론트엔드와 동일한 네트워크에서 개발 시 별도 CORS 설정 필요 없음

---

## 2. 프론트엔드

### 기술 스택

- **React** (Create React App 기반)
- JavaScript (ES6+)
- React Router
- CSS

### 주요 구조

- `src/App.jsx`: 메인 컴포넌트, 상태 관리 및 라우팅
- `src/LeaderboardPage.js`: 리더보드(모델 랭킹) 페이지
- `src/index.js`: 앱 진입점
- `src/index.css`, `src/App.css`: 스타일
- `public/index.html`: HTML 템플릿

### 실행 방법

1. 의존성 설치  
   ```
   npm install
   ```

2. 개발 서버 실행  
   ```
   npm start
   ```
   [http://localhost:3000](http://localhost:3000)에서 확인 가능

3. 테스트 실행  
   ```
   npm test
   ```

4. 프로덕션 빌드  
   ```
   npm run build
   ```

5. eject (설정 분리, 되돌릴 수 없음)  
   ```
   npm run eject
   ```

- 자세한 사용법 및 추가 문서는 [Create React App 공식 문서](https://facebook.github.io/create-react-app/docs/getting-started) 참고

---

## 프로젝트 구조 예시

```
openpatientpsi/
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── models/
│   ├── patient_example.json
│   └── ...
└── README.md
```

---

## 참고

- 프론트엔드와 백엔드는 각기 독립적으로 실행합니다.
- 추가적인 모델은 `backend/models/registry.py`에 등록하여 확장할 수 있습니다.
- 이 저장소는 연구 및 실험 목적에 적합하며, 실제 서비스 적용 시 보안, 인증 등 추가 개발이 필요합니다.

---