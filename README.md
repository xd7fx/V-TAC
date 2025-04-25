

# ⚽ V-TAC: Vision Tactical AI Coach

![V-TAC Overview](https://github.com/user-attachments/assets/03a0fe80-a9b9-43fe-8b26-a1c64b95e47c)

## 🌟 Overview

**V-TAC (Vision Tactical AI Coach)** is a next-generation football AI system that offers accurate pre-match predictions, live tactical decisions, and fatigue-aware substitution advice. Designed for analysts and coaches, V-TAC combines machine learning, real-time API data, and a chatbot interface.

---

## ⚖️ Data Collection & Preparation

### ✅ Data Sources
- **Match Data**: 70,000+ games from [API-Football](https://www.api-football.com)
- **Player Data**: 120,000+ player records with live stats (passes, tackles, fatigue)
- Leagues: Premier League, La Liga, Bundesliga, Serie A, Saudi Pro League, etc.

### ⚙️ Preprocessing Pipeline
- Merging data across seasons
- Cleaning missing values
- Feature engineering (recent form, H2H, xG, formation success)
- Encoding teams/formations
- Scaling using `StandardScaler`

![image](https://github.com/user-attachments/assets/c3a70e90-44c8-4523-aaf2-ed8855b88a71)

---

## 🤖 Core AI Models

### 1️⃣ Pre-Match Outcome Prediction
- **Goal**: Predict Win/Draw/Loss before kickoff
- **Model**: AutoGluon.Tabular
- **Type**: Multiclass classification
- **Features**: team rank, points, pass %, goals, form, formation, H2H
- **Accuracy**: ~77% after oversampling

![Pre-Match Accuracy](https://github.com/user-attachments/assets/e4feb2c4-e18a-42d9-9b05-863c3a0b3440)  
![Feature Impact](https://github.com/user-attachments/assets/5c487c62-ff76-4058-9870-140fd545323e)

---

### 2️⃣ Live Match Outcome Prediction (Every 5 Minutes)
- **Goal**: Update predictions live using real-time stats
- **Model**: AutoGluon + real-time snapshot
- **Data**: goals, possession, shots, pass %, formation, momentum
- **Metric**: Log loss < 0.27

![Charts](https://github.com/user-attachments/assets/895f25ca-19e6-45b8-b3cc-98145d6cf9da)  
![Prediction Curves](https://github.com/user-attachments/assets/dc3b88c4-c6bc-4203-904d-566bb33a401a)




Example:
```
Chelsea → Win: 63% | Draw: 25% | Loss: 12%
Recommendation: ✅ Keep the formation, momentum is high.
```

![Live UI](https://github.com/user-attachments/assets/d5702d96-657c-4633-9b5d-f84f6c7995d8)  

---

### 3️⃣ Player Fatigue Estimator
- **Goal**: Detect when a player is too tired
- **Inputs**: minutes, passes, duels, distance covered
- **Output**: fatigue score (0 to 1)
- **Frequency**: every 5 minutes for each player
- **Accuracy**: ~97% 


![download](https://github.com/user-attachments/assets/337dc056-45c3-44be-9292-20f658f2be70)

---

## 🧭 Recommendation & Interface Components

### 4️⃣ Formation Suggestion Engine
- Type: Rule-based
- Recommends the best formation historically vs opponent
```
Best Formation: 4-2-3-1
→ vs 4-3-3 = 70% win rate
```
![Tactical Panel](https://github.com/user-attachments/assets/ea4371f9-c8ca-4aa7-b0c7-130bbcdf4c1f)  

---

### 5️⃣ AI Chatbot (LLM-powered)
- Based on **OpenChat / DeepSeek**
- Answers tactical questions using real predictions
- Live updates trigger smart language output
```
"Switch to 4-4-2, midfield fatigue is increasing."
```

---

### 6️⃣ CSV Agent (LangChain)
- Used for QA over match/player CSVs
- Helpful during model validation/debugging


---

### 7️⃣ 3D Avatar + Edge-TTS + Rhubarb Lip Sync
- **TTS**: Converts predictions to voice
- **Lip Sync**: Generates visemes using Rhubarb
- **3D Avatar**: Visual face for match recommendations


---

## 🔁 Real-Time Architecture Flow

![image](https://github.com/user-attachments/assets/ae17cb3e-f714-4f5b-a359-4acba8070a14)

- ⏱ Updates every 5 mins during match
- 📥 Sends outputs to Chatbot / Avatar
- 🔁 After match: update training data + fine-tune model

---

## 💻 UI/UX (Figma Preview)

[🔗 View Prototype](https://www.figma.com/proto/cMnlbXuyIG1liGdh1vhMMY/V-TAC)

![Figma 1](https://github.com/user-attachments/assets/58144ca0-7e3c-49bc-b438-3d0b44314ab8)  
![Figma 2](https://github.com/user-attachments/assets/8b1e6ede-769a-4e9d-bd66-8257a5be931d)  
![Figma 3](https://github.com/user-attachments/assets/f1296340-b97b-4e8b-8fe0-93afdb9d51d4) 
![image](https://github.com/user-attachments/assets/f85ca1f2-d9b1-4f10-a6cc-2b4bdb06bf8f)
![image](https://github.com/user-attachments/assets/2118bc4b-9367-43d0-a729-4df7f1ee8af7)

---

## 🧠 AI Tech Stack

| Layer               | Technology                  |
|---------------------|------------------------------|
| Model Training      | AutoGluon, Scikit-learn      |
| Real-Time Updates   | API-Football + custom logic  |
| Data Interaction    | LangChain CSV Agent          |
| Voice Interaction   | Edge-TTS + Rhubarb           |
| Avatar Interface    | React + Flask                |
| Language Model      | OpenChat                     |

---

## 👥 Team

| Name                 | Role                        |
|----------------------|-----------------------------|
| Abdulrahman AlNashri | AI Modeling + UI/UX         |
| Osama AlGhamdi       | AI Modeling + Sport         |
| Rawaa AlTurkistani   | Security + Presentations    |
| Ghadir Najm          | Business + Coordination     |

---

## 🚀 What's Next?
- 🎮 GPS/IMU sensors for live fatigue
- 📊 Deep learning for player embeddings
- 🧠 Fully autonomous LLM assistant
- ⚽ Deployment in real matches with clubs
