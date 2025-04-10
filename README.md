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

### 🖼️ Feature Importance (Insert image here)
`[Insert feature_importance.png]`

### 🎨 Match Result Visualization (Optional)
`[Insert confusion_matrix.png]`

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
`[Insert win_curve_team1.png]`
`[Insert win_curve_team2.png]`

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

## 📅 Project Structure
```
├── data/
│   └── all_data_with_rank_and_point.csv
├── model_1.ipynb  # Pre-Match Model
├── model_2.ipynb  # Live Match Model
├── utils/
│   └── feature_engineering.py
├── assets/
│   ├── feature_importance.png
│   ├── win_curve_team1.png
│   ├── confusion_matrix.png
└── README.md
```

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

---

## ❤️ Support
Have questions or want to collaborate?
- Contact: **vtac@sportai.com**
- License: MIT

