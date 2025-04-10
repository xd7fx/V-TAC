# V-TAC: AI-Powered Football Match Prediction and Tactical Assistant

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

## 🏆 Model 1: Pre-Match Prediction
### Goal
Predict the result of the match before it starts.

### Framework
- Uses `AutoGluon.TabularPredictor`
- Classification: Multiclass (Win = 1, Draw = 0.5, Loss = 0)
- Evaluation Metric: `log_loss`

### Feature Set
Over 40 features including:
- Team & opponent ranks
- Average goals scored/conceded (last 5)
- Recent win/draw/loss ratios
- Possession, pass accuracy, shots, corners
- Formation success rates
- H2H historical data

### Results
| Metric       | Value        |
|--------------|--------------|
| Accuracy     | ~77%         |
| Log Loss     | < 0.45       |

### 🖼️ Confusion Matrix (Insert image here)
![image_2025-04-10_12-02-15](https://github.com/user-attachments/assets/830a576c-f6c8-4b92-b650-8b1f954c023f)

### 🎨 Match Result Visualization (Optional)
![image_2025-04-10_12-01-52](https://github.com/user-attachments/assets/582829bb-1840-4fde-a51c-13d01257a857)

---

## ⏱️ Model 2: Live Match Prediction (Real-time)
### Goal
Predict win/draw/loss probabilities every 5 minutes during a match and provide tactical advice.

### Input
Live match snapshot including:
- Current formations
- Possession, passing, goals
- Updated ranks & points

### Processing
- Match data is converted to team-level format
- Same features used as pre-match model
- Scaled using pre-trained `StandardScaler`
- Passed to saved AutoGluon model

### Output Example
```text
🕟 15:00
🏟️ Chelsea → Win: 61%, Draw: 24%, Loss: 15%
🏟️ Brentford → Win: 23%, Draw: 30%, Loss: 47%
📅 Recommendation: ⚡ Time to apply pressure. Try offensive subs.
```

### 📈 Win Probability Curve

![image (1)](https://github.com/user-attachments/assets/a79735b3-df86-4089-8fb5-57f7d667c853)

![image](https://github.com/user-attachments/assets/1682ed97-056a-4db3-9ee2-aaea4f469626)

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
![image](https://github.com/user-attachments/assets/fc5ad310-4a2c-4dcc-85fb-55c0f9a69407)


---

## 🏢 User Interface (Future Vision)
### Main Dashboard
- 🏆 Pre-Match Prediction Button
- ⏱️ Live Match Mode (Auto updates every 5 mins)
- 🔬 Tactical Recommendation Section
- 🤖 AI Chat Assistant Access

### Interface Visual Example:
`[Insert dashboard_mockup.png]`

---

## 🌐 Try It Out
- Load your match CSV with rank + points
- Run `model_1.ipynb` or `model_2.ipynb`
- Visualize match predictions and curves

---

## 💼 Authors
- **@Mehdhar** – Data & AI Engineer
- **V-TAC Team** – Vision & Tactical Experts

---

## 🚀 Next Steps
- 📉 Integrate GPS/IMU fatigue detection
- 🏋️ Player-level performance modeling
- 🤖 Full deployment of V-TAC as an LLM assistant
- 🏅 Real-world testing with clubs


