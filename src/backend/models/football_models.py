import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report
from autogluon.tabular import TabularPredictor
import joblib

from process_module import (
    PreMatchProcessor,
    LiveMatchProcessor,
    FatigueProcessor,
    compute_recent_form,
    convert_to_team_level_live
)



class PreMatchModel:
    def __init__(self, model_path="models/", data_path="data/merged_all_data_2016_2024.csv"):
        self.model_path = model_path
        self.data_path = data_path
        self.processor = PreMatchProcessor()
        self.predictor = None

    def train(self):
        df = self.processor.load_and_process(self.data_path)
        df = df.sort_values("date").reset_index(drop=True)
        train_data, test_data = train_test_split(df, test_size=0.2, shuffle=False)

        self.predictor = TabularPredictor(label="team_result", path=self.model_path).fit(
            train_data=train_data,
            presets="best_quality",
            hyperparameters={
                'CAT': {
                    'iterations': 1000,
                    'learning_rate': 0.03,
                    'depth': 8,
                    'l2_leaf_reg': 3
                },
                'XGB': {
                    'n_estimators': 1000,
                    'learning_rate': 0.03,
                    'max_depth': 8,
                    'subsample': 0.9,
                    'colsample_bytree': 0.8
                },
                'GBM': [{
                    'learning_rate': 0.03,
                    'num_leaves': 128,
                    'feature_fraction': 0.9,
                    'min_data_in_leaf': 3,
                    'ag_args': {
                        'name_suffix': 'Large',
                        'priority': 1,
                        'hyperparameter_tune_kwargs': None
                    }
                }]
            }
        )

        performance = self.predictor.evaluate(test_data)
        print("✅ Model Performance:", performance)

        X_test = test_data.drop(columns=["team_result"])
        y_test = test_data["team_result"]
        y_pred = self.predictor.predict(X_test)

        cm = confusion_matrix(y_test, y_pred, labels=["Win", "Draw", "Loss"])
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Win", "Draw", "Loss"])
        disp.plot(cmap="Blues", values_format="d")
        plt.title("Confusion Matrix - Test Set")
        plt.show()

        self.predictor.feature_importance(test_data)

    def load(self):
        self.predictor = TabularPredictor.load(self.model_path)

    def predict(self, csv_path):
        df = self.processor.load_and_process(csv_path)
        X = df.drop(columns=["team_result"], errors='ignore')
        preds = self.predictor.predict(X)
        probs = self.predictor.predict_proba(X)
        return pd.concat([df[["fixture_id", "team_name", "opponent_name"]], preds, probs], axis=1)





class LiveMatchModel:
    def __init__(self, model_path="models/"):
        self.model_path = model_path
        self.processor = LiveMatchProcessor()
        self.predictor = None

    def train(self, path="data/all_data_with_rank_and_point.csv"):
        df = self.processor.load_and_process(path)

        features = [
            'season', 'league', 'game_week', 'team', 'opponent', 'is_home',
            'team_formation', 'team_form_win_rate',
            'opponent_formation', 'opponent_form_win_rate',
            'team_shots_on_target', 'team_shots', 'team_fouls', 'team_corners',
            'team_offsides', 'team_possession', 'team_yellow_cards', 'team_red_cards',
            'team_saves', 'team_pass_accuracy',
            'opponent_shots_on_target', 'opponent_shots', 'opponent_fouls', 'opponent_corners',
            'opponent_offsides', 'opponent_possession', 'opponent_yellow_cards', 'opponent_red_cards',
            'opponent_saves', 'opponent_pass_accuracy',
            'recent_wins', 'recent_draws', 'recent_losses',
            'team_rank', 'opponent_rank', 'team_points', 'opponent_points',
            'team_rank_dif', 'opponent_rank_dif', 'team_points_dif', 'opponent_points_dif'
        ]

        df = df[features + ['team_win']].dropna()
        train_data = df.sample(frac=0.8, random_state=42)
        test_data = df.drop(train_data.index)

        self.predictor = TabularPredictor(label="team_win", problem_type="multiclass", eval_metric="log_loss", path=self.model_path)
        self.predictor.fit(train_data)

        print("✅ Evaluation:")
        print(self.predictor.evaluate(test_data))
        print("\n🏆 Leaderboard:")
        print(self.predictor.leaderboard(test_data, silent=True)[['model', 'score_val']])

    def predict(self, snapshot_path, historical_path, team_info):
        df_snapshot = pd.read_csv(snapshot_path)
        df_historical = pd.read_csv(historical_path)

        # Add rank & points
        def get_rank(team): return team_info.get(team, {}).get('rank', np.nan)
        def get_points(team): return team_info.get(team, {}).get('points', np.nan)

        df_snapshot['home_rank'] = df_snapshot['home_team'].apply(get_rank)
        df_snapshot['away_rank'] = df_snapshot['away_team'].apply(get_rank)
        df_snapshot['home_points'] = df_snapshot['home_team'].apply(get_points)
        df_snapshot['away_points'] = df_snapshot['away_team'].apply(get_points)

        # Differences
        for df in [df_snapshot, df_historical]:
            df['home_rank_dif'] = df['home_rank'] - df['away_rank']
            df['away_rank_dif'] = -df['home_rank_dif']
            df['home_points_dif'] = df['home_points'] - df['away_points']
            df['away_points_dif'] = -df['home_points_dif']

        # Convert to team level
        snapshot_team = convert_to_team_level_live(df_snapshot)
        snapshot_team['timestamp'] = pd.concat([df_snapshot['timestamp'], df_snapshot['timestamp']]).reset_index(drop=True)

        # Fill missing values
        fill_zero = ['team_red_cards', 'team_yellow_cards', 'team_saves', 'opponent_red_cards', 'opponent_yellow_cards', 'opponent_saves', 'team_offsides', 'opponent_offsides', 'team_attempted_passes', 'opponent_attempted_passes']
        for col in fill_zero:
            snapshot_team[col] = snapshot_team[col].fillna(0)

        for col in ['team_possession', 'opponent_possession']:
            snapshot_team[col] = snapshot_team[col].astype(str).str.replace('%', '', regex=False).astype(float)

        snapshot_team['team_pass_accuracy'] = (snapshot_team['team_attempted_passes'] / snapshot_team['team_attempted_passes']).fillna(0)
        snapshot_team['opponent_pass_accuracy'] = (snapshot_team['opponent_successful_passes'] / snapshot_team['opponent_attempted_passes']).fillna(0)
        snapshot_team.drop(columns=['team_successful_passes', 'opponent_successful_passes'], inplace=True)

        # Load encoders
        snapshot_team['team'] = joblib.load("models/le_team.pkl").transform(snapshot_team['team'])
        snapshot_team['opponent'] = joblib.load("models/le_opp.pkl").transform(snapshot_team['opponent'])
        snapshot_team['team_formation'] = joblib.load("models/le_form_team.pkl").transform(snapshot_team['team_formation'])
        snapshot_team['opponent_formation'] = joblib.load("models/le_form_opp.pkl").transform(snapshot_team['opponent_formation'])

        # Form win rate
        full_team = convert_to_team_level_live(df_historical)
        full_team['team_win'] = (full_team['team_goals'] > full_team['opponent_goals']).astype(int)

        team_form_win_rate = full_team.groupby('team_formation')['team_win'].mean().to_dict()
        opp_form_win_rate = full_team.groupby('opponent_formation')['team_win'].apply(lambda x: 1 - x.mean()).to_dict()
        snapshot_team['team_form_win_rate'] = snapshot_team['team_formation'].map(team_form_win_rate).fillna(0.5)
        snapshot_team['opponent_form_win_rate'] = snapshot_team['opponent_formation'].map(opp_form_win_rate).fillna(0.5)

        snapshot_team = compute_recent_form(snapshot_team)

        # Scale features
        scaler = joblib.load("models/scaler.pkl")
        scale_cols = list(scaler.feature_names_in_)
        snapshot_team[scale_cols] = pd.DataFrame(
            scaler.transform(snapshot_team[scale_cols]),
            columns=scale_cols,
            index=snapshot_team.index
        )

        predictor = TabularPredictor.load(self.model_path)
        features = scale_cols + ['season', 'league', 'game_week', 'team', 'opponent', 'is_home', 'team_formation', 'opponent_formation']
        preds = predictor.predict_proba(snapshot_team[features])

        return preds



class FatigueModel:
    def __init__(self, model_path="models/", data_path="data/players_detailed_all_fixtures_fixed.csv"):
        self.model_path = model_path
        self.data_path = data_path
        self.processor = FatigueProcessor()
        self.predictor = None

    def train(self):
        df = self.processor.load_and_process(self.data_path)
        train_data, test_data = train_test_split(df, test_size=0.2, random_state=42, shuffle=True)

        self.predictor = TabularPredictor(label="is_fatigued", path=self.model_path, problem_type="binary")
        self.predictor.fit(train_data)

        print("✅ Evaluation:")
        print(self.predictor.evaluate(test_data))

        y_true = test_data["is_fatigued"]
        y_pred = self.predictor.predict(test_data.drop(columns=["is_fatigued"]))
        print("\n📊 Classification Report:")
        print(classification_report(y_true, y_pred))

    def load(self):
        self.predictor = TabularPredictor.load(self.model_path)

    def predict(self, csv_path):
        df = self.processor.load_and_process(csv_path)
        preds = self.predictor.predict(df.drop(columns=["is_fatigued"], errors='ignore'))
        probs = self.predictor.predict_proba(df.drop(columns=["is_fatigued"], errors='ignore'))[1]
        df["fatigue_prediction"] = preds
        df["fatigue_probability"] = probs
        return df.sort_values("fatigue_probability", ascending=False)
