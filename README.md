# V-TAC: AI-Powered Football Match Prediction and Tactical Assistant
![_⁨صورة PNG⁩](https://github.com/user-attachments/assets/03a0fe80-a9b9-43fe-8b26-a1c64b95e47c)

## 🌟 Overview
**V-TAC (Virtual Tactical Assistant Coach)** is a football intelligence system that leverages AI to provide accurate match outcome predictions and real-time tactical recommendations for coaches. It consists of two core models:

- **Pre-Match Model**: Predicts win/draw/loss outcome using historical data.
- **Live Match Model**: Predicts live outcomes every 5 minutes and suggests tactical decisions.

The system is powered by **AutoGluon**, enriched with real-world API data, and optimized for practical coaching support.

---

## ⚖️ Data Collection & Preparation
### ✅ Match Data Source
- Collected from **API-Football** (2016-2023)
- Leagues: Premier League, La Liga, Serie A, Bundesliga, Saudi Pro League
- Includes over **50,000 matches**

### ⚙️ Preprocessing Steps
1. **Data Merging**: All leagues & seasons combined
2. **Data Cleaning**:
   - Fill missing values (shots, cards, passes...)
   - Convert % fields (possession)
3. **Encoding**: Teams, formations, leagues, seasons
4. **Feature Engineering**:
   - Team & Opponent stats separately (shots, passes, corners)
   - Formation win rates
   - Recent form (wins, draws, losses)
   - Average goals, pass accuracy, possession (last 5 matches)
   - Head-to-head stats
   - Rank and point differences
5. **Scaling**: Using `StandardScaler` for numeric features

---

## 🏟️ Model 1: Pre-Match Outcome Prediction

### 🎯 Goal
Predict the match result before kickoff using historical team stats, ranks, and performance trends.

### ⚙️ Framework
- Library: AutoGluon.Tabular
- Type: Multiclass Classification (1 = Win, 0.5 = Draw, 0 = Loss)
- Metric: Accuracy

### 📊 Feature Set (~40 total)
- Team & opponent ranks, points
- Recent performance (last 5 matches): wins, draws, losses
- Average goals scored & conceded
- Possession, corners, shots, pass accuracy
- Formations & their success rates
- Head-to-head win/draw/loss rates

### 📈 Performance
- **Accuracy after oversampling**: ~77%
- **Model used**: AutoGluon.Tabular with tuning

![image_2025-04-10_12-02-15](https://github.com/user-attachments/assets/e4feb2c4-e18a-42d9-9b05-863c3a0b3440)
![image_2025-04-10_12-01-52](https://github.com/user-attachments/assets/5c487c62-ff76-4058-9870-140fd545323e)

---

## 🥅 Model 2: In-Match Live Outcome Prediction

### 🎯 Goal
Predict match outcome every 5 minutes during the match using live stats + team formations.

### ⚙️ Framework
- Library: AutoGluon.Tabular
- Type: Multiclass Classification (1 = Win, 0.5 = Draw, 0 = Loss)
- Metric: log_loss

### 🧠 Features (~40+)
- Current goals, formations, updated pass/shots/possession
- Team rank, points (live updated)
- Recent form (last 5 matches)
- Formation win-rate, live momentum shifts

### 🔁 Real-Time Prediction
- Predictions are made for each team separately
- Output: Probabilities for Win / Draw / Loss
- Displayed with timestamped recommendations for tactical action

#### 🧪 Example
```
Chelsea → Win: 63% | Draw: 25% | Loss: 12%
Recommendation: ✅ Keep the formation, momentum is high.
```
![image](https://github.com/user-attachments/assets/d5702d96-657c-4633-9b5d-f84f6c7995d8)
![image](https://github.com/user-attachments/assets/ea4371f9-c8ca-4aa7-b0c7-130bbcdf4c1f)


### 📈 Performance
- **Log Loss**: < 0.3

![image](https://github.com/user-attachments/assets/895f25ca-19e6-45b8-b3cc-98145d6cf9da)
![image (1)](https://github.com/user-attachments/assets/dc3b88c4-c6bc-4203-904d-566bb33a401a)



---
## 📊 Model Comparison
| Feature                                 | Pre-Match Model | Live Match Model |
|-----------------------------------------|-----------------|------------------|
| Data source                             | Historical      | Live (snapshot)  |
| Update frequency                        | Once            | Every 5 mins     |
| Tactical recommendation                 | ✅ Yes         | ✅ Yes          |
| Predictive accuracy                     | High            | Adaptive         |
| Use case                                | Planning        | In-game coaching |

---

## 🔍 Tactical Intelligence Engine
### 👉 Formation Recommendation
Recommends the **most effective formation** based on win rate history vs opponent formation.
```text
🌟 Best Formation: 4-2-3-1 (Win rate: 65%)
🔹 Best vs 4-3-3 → 70% win rate
```

### 🤖 AI Chat Integration
Smart assistant gives natural language advice to the coach:
- "Try switching to 4-4-2 to counter midfield control"
- "Increase pressing intensity; possession dropping"

---

## 📅 UI / UX

try https://www.figma.com/proto/cMnlbXuyIG1liGdh1vhMMY/V-TAC?node-id=14-73&p=f&t=bnZt3raZhrZ4YcC4-0&scaling=scale-down&content-scaling=fixed&page-id=0%3A1
![image](https://github.com/user-attachments/assets/58144ca0-7e3c-49bc-b438-3d0b44314ab8)
![image](https://github.com/user-attachments/assets/8b1e6ede-769a-4e9d-bd66-8257a5be931d)
![image](https://github.com/user-attachments/assets/f1296340-b97b-4e8b-8fe0-93afdb9d51d4)
![image](https://github.com/user-attachments/assets/55b32dd4-ec6b-490f-9abd-8ef2720fc477)
![image](https://github.com/user-attachments/assets/354666d2-75c0-46fe-bc85-f22c8f5f0ff7)

---

## 🏢 User Interface (Future Vision)
### Main Dashboard
- 🏆 Pre-Match Prediction Button
- ⏱️ Live Match Mode (Auto updates every 5 mins)
- 🔬 Tactical Recommendation Section
- 🤖 AI Chat Assistant Access
---

## 🌐 Try It Out
- Load your match CSV with rank + points
- Run `model_1.ipynb` or `model_2.ipynb`
- Visualize match predictions and curves

---

## 💼 Authors

| Name                 | Specialty                      | Role                             |
|----------------------|--------------------------------|----------------------------------|
| **Abdulrahman AlNashri** | AI & UI/UX Design          | Model Building & UI/UE           |
| **Osama AlGhamdi**   |  AI & Sports                   | Model Building & Analysis        |
| **Rawaa AlTurkistani** | Cybersecurity                  | Presentation & Security          |
| **Ghadir Najm**      | Cybersecurity                  | Business Model                   |



---

## 🚀 Next Steps
- 📉 Integrate GPS/IMU fatigue detection
- 🏋️ Player-level performance modeling
- 🤖 Full deployment of V-TAC as an LLM assistant
- 🏅 Real-world testing with clubs
