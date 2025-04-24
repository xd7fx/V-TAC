import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib



class PreMatchProcessor:
    def __init__(self, window=5):
        self.window = window

    def load_and_process(self, path):
        df = pd.read_csv(path)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.dropna(subset=['date'], inplace=True)
        df = self.fill_missing_values(df)
        df = self.clean_formations(df)
        df = self.clean_possession(df)
        df_team = self.convert_to_team_level(df)
        df_sorted = self.compute_recent_win_rate(df_team)
        df_sorted = self.compute_avg_goals(df_sorted)
        df_sorted['goal_difference'] = df_sorted['avg_goals_for'] - df_sorted['avg_goals_against']
        df_final = self.merge_features(df_team, df_sorted)
        df_final = self.add_opponent_features(df_final)
        df_final = self.compute_points_and_ranks(df_final)
        df_final = self.compute_h2h_rates(df_final)
        df_final = self.final_cleaning(df_final)
        return df_final

    def fill_missing_values(self, df):
        df['home_rank'] = df.groupby(['league', 'season'])['home_rank'].transform(lambda x: x.fillna(x.mean()))
        df['away_rank'] = df.groupby(['league', 'season'])['away_rank'].transform(lambda x: x.fillna(x.mean()))
        df['home_points'] = df.groupby(['league', 'season'])['home_points'].transform(lambda x: x.fillna(x.mean()))
        df['away_points'] = df.groupby(['league', 'season'])['away_points'].transform(lambda x: x.fillna(x.mean()))
        df['home_offsides'] = df['home_offsides'].fillna(0)
        df['away_offsides'] = df['away_offsides'].fillna(0)
        df['home_red_cards'] = df['home_red_cards'].fillna(0)
        df['away_red_cards'] = df['away_red_cards'].fillna(0)
        df['home_yellow_cards'] = df.groupby(['league', 'season'])['home_yellow_cards'].transform(lambda x: x.fillna(x.mean()))
        df['away_yellow_cards'] = df.groupby(['league', 'season'])['away_yellow_cards'].transform(lambda x: x.fillna(x.mean()))
        df['home_goalkeeper_saves'] = df.groupby(['league', 'season'])['home_goalkeeper_saves'].transform(lambda x: x.fillna(x.mean()))
        df['away_goalkeeper_saves'] = df.groupby(['league', 'season'])['away_goalkeeper_saves'].transform(lambda x: x.fillna(x.mean()))
        for col in ['home_attempted_passes', 'home_successful_passes', 'away_attempted_passes', 'away_successful_passes']:
            df[col] = df.groupby(['league', 'season'])[col].transform(lambda x: x.fillna(x.mean()))
        df['home_corners'] = df.groupby(['league', 'season'])['home_corners'].transform(lambda x: x.fillna(x.mean()))
        df['away_corners'] = df.groupby(['league', 'season'])['away_corners'].transform(lambda x: x.fillna(x.mean()))
        df['home_shots'] = df.groupby(['league', 'season'])['home_shots'].transform(lambda x: x.fillna(x.mean()))
        df['away_shots'] = df.groupby(['league', 'season'])['away_shots'].transform(lambda x: x.fillna(x.mean()))
        return df

    def clean_formations(self, df):
        df['home_formation'] = df['home_formation'].fillna('Unknown')
        df['away_formation'] = df['away_formation'].fillna('Unknown')
        return df

    def clean_possession(self, df):
        for col in ['home_possession', 'away_possession']:
            df[col] = df[col].astype(str).str.replace('%', '').astype(float)
        return df

    def convert_to_team_level(self, df):
        team_rows = []
        for _, row in df.iterrows():
            for is_home in [1, 0]:
                prefix = 'home_' if is_home else 'away_'
                opponent_prefix = 'away_' if is_home else 'home_'
                team_row = {
                    'fixture_id': row['fixture_id'],
                    'league': row['league'],
                    'season': row['season'],
                    'date': row['date'],
                    'is_home': is_home,
                    'team_name': row[prefix + 'team'],
                    'opponent_name': row[opponent_prefix + 'team'],
                    'team_goals': row[prefix + 'goals'],
                    'opponent_goals': row[opponent_prefix + 'goals'],
                    'team_rank': row[prefix + 'rank'],
                    'opponent_rank': row[opponent_prefix + 'rank'],
                    'team_points': row[prefix + 'points'],
                    'opponent_points': row[opponent_prefix + 'points'],
                    'team_formation': row[prefix + 'formation'],
                    'opponent_formation': row[opponent_prefix + 'formation'],
                }
                for stat in ['shots', 'shots_on_target', 'possession', 'goalkeeper_saves',
                             'yellow_cards', 'red_cards', 'corners', 'fouls', 'offsides',
                             'attempted_passes', 'successful_passes']:
                    team_row[f'team_{stat}'] = row[prefix + stat]
                    team_row[f'opponent_{stat}'] = row[opponent_prefix + stat]
                team_rows.append(team_row)
        df_team = pd.DataFrame(team_rows)
        df_team['team_result'] = df_team.apply(
            lambda x: 'Win' if x['team_goals'] > x['opponent_goals'] else ('Loss' if x['team_goals'] < x['opponent_goals'] else 'Draw'),
            axis=1
        )
        return df_team

    def compute_recent_win_rate(self, df):
        df = df.copy()
        df['result_numeric'] = df['team_result'].map({'Win': 1.0, 'Draw': 0.5, 'Loss': 0.0})
        df['recent_win_rate'] = df.groupby(['league', 'season', 'team_name'])['result_numeric'].transform(
            lambda x: x.shift().rolling(self.window, min_periods=1).mean())
        df.drop(columns=['result_numeric'], inplace=True)
        return df

    def compute_avg_goals(self, df):
        df = df.copy()
        df['avg_goals_for'] = df.groupby(['league', 'season', 'team_name'])['team_goals'].transform(
            lambda x: x.shift().rolling(self.window, min_periods=1).mean())
        df['avg_goals_against'] = df.groupby(['league', 'season', 'team_name'])['opponent_goals'].transform(
            lambda x: x.shift().rolling(self.window, min_periods=1).mean())
        return df

    def merge_features(self, df_base, df_features):
        df_base['index_row'] = df_base.reset_index().index
        merged = pd.merge(
            df_base,
            df_features[['fixture_id', 'is_home', 'team_name', 'recent_win_rate',
                         'avg_goals_for', 'avg_goals_against', 'goal_difference']],
            on=['fixture_id', 'is_home', 'team_name'],
            how='left'
        )
        return merged.sort_values('index_row').drop(columns='index_row').reset_index(drop=True)

    def add_opponent_features(self, df):
        opp_df = df[['fixture_id', 'is_home', 'team_name', 'recent_win_rate',
                     'avg_goals_for', 'goal_difference']].copy()
        opp_df['is_home'] = 1 - opp_df['is_home']
        opp_df = opp_df.rename(columns={
            'team_name': 'opponent_name',
            'recent_win_rate': 'opponent_recent_win_rate',
            'avg_goals_for': 'opponent_avg_goals_for',
            'goal_difference': 'opponent_goal_difference'
        })
        return pd.merge(df, opp_df, on=['fixture_id', 'is_home', 'opponent_name'], how='left')

    def compute_points_and_ranks(self, df):
        df = df.copy().sort_values(by=['league', 'season', 'date']).reset_index(drop=True)
        df['team_points'] = np.nan
        df['opponent_points'] = np.nan
        df['team_rank'] = np.nan
        df['opponent_rank'] = np.nan
        for (league, season), group in df.groupby(['league', 'season']):
            points_table = {}
            for i, row in group.iterrows():
                team = row['team_name']
                opponent = row['opponent_name']
                team_pts = points_table.get(team, 0)
                opponent_pts = points_table.get(opponent, 0)
                df.loc[i, 'team_points'] = team_pts
                df.loc[i, 'opponent_points'] = opponent_pts
                ranks = {team_name: rank+1 for rank, (team_name, _) in enumerate(sorted(points_table.items(), key=lambda x: -x[1]))}
                df.loc[i, 'team_rank'] = ranks.get(team, np.nan)
                df.loc[i, 'opponent_rank'] = ranks.get(opponent, np.nan)
                if row['team_result'] == 'Win':
                    points_table[team] = team_pts + 3
                elif row['team_result'] == 'Draw':
                    points_table[team] = team_pts + 1
                    points_table[opponent] = opponent_pts + 1
                elif row['team_result'] == 'Loss':
                    points_table[opponent] = opponent_pts + 3
        return df

    def compute_h2h_rates(self, df):
        df = df.sort_values(by='date').copy()
        for col in ['h2h_home_win_rate', 'h2h_home_draw_rate', 'h2h_home_loss_rate']:
            df[col] = np.nan
        grouped = df.groupby(['team_name', 'opponent_name'])
        for _, group in grouped:
            for i in range(len(group)):
                past = group.iloc[max(0, i - self.window):i]
                total = len(past)
                wins = (past['team_result'] == 'Win').sum()
                draws = (past['team_result'] == 'Draw').sum()
                losses = (past['team_result'] == 'Loss').sum()
                df.loc[group.index[i], 'h2h_home_win_rate'] = wins / total if total else np.nan
                df.loc[group.index[i], 'h2h_home_draw_rate'] = draws / total if total else np.nan
                df.loc[group.index[i], 'h2h_home_loss_rate'] = losses / total if total else np.nan
        return df

    def final_cleaning(self, df):
        df = df.fillna({
            'h2h_home_win_rate': 0.5,
            'h2h_home_draw_rate': 0.3,
            'h2h_home_loss_rate': 0.2
        })
        df['team_result'] = df['team_result'].astype('category')
        df = df.drop(columns=['team_goals', 'opponent_goals', 'goal_difference'])
        df['date'] = pd.to_datetime(df['date'])
        rolling_cols = [
            'team_shots', 'team_shots_on_target', 'team_goalkeeper_saves', 'team_possession',
            'team_corners', 'team_fouls', 'team_yellow_cards', 'team_red_cards', 'team_offsides',
            'team_attempted_passes', 'team_successful_passes', 'opponent_shots',
            'opponent_shots_on_target', 'opponent_goalkeeper_saves', 'opponent_possession',
            'opponent_corners', 'opponent_fouls', 'opponent_yellow_cards', 'opponent_red_cards',
            'opponent_offsides', 'opponent_attempted_passes', 'opponent_successful_passes'
        ]
        for col in rolling_cols:
            base = 'team_name' if col.startswith('team_') else 'opponent_name'
            df[col + '_avg'] = df.sort_values('date').groupby(['league', 'season', base])[col].transform(
                lambda x: x.shift().rolling(self.window, min_periods=1).mean())
        df.drop(columns=rolling_cols, inplace=True)
        return df


class LiveMatchProcessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.le_team = LabelEncoder()
        self.le_opp = LabelEncoder()
        self.le_form_team = LabelEncoder()
        self.le_form_opp = LabelEncoder()

    def convert_to_team_level_live(self, df):
        shared_cols = ['fixture_id', 'league', 'season', 'date', 'stadium', 'game_week']
        if 'timestamp' in df.columns:
            shared_cols.append('timestamp')

        team_cols = {
            'home_team': 'team', 'away_team': 'opponent',
            'home_goals': 'team_goals', 'away_goals': 'opponent_goals',
            'home_shots_on_target': 'team_shots_on_target', 'away_shots_on_target': 'opponent_shots_on_target',
            'home_shots': 'team_shots', 'away_shots': 'opponent_shots',
            'home_fouls': 'team_fouls', 'away_fouls': 'opponent_fouls',
            'home_corners': 'team_corners', 'away_corners': 'opponent_corners',
            'home_offsides': 'team_offsides', 'away_offsides': 'opponent_offsides',
            'home_possession': 'team_possession', 'away_possession': 'opponent_possession',
            'home_yellow_cards': 'team_yellow_cards', 'away_yellow_cards': 'opponent_yellow_cards',
            'home_red_cards': 'team_red_cards', 'away_red_cards': 'opponent_red_cards',
            'home_goalkeeper_saves': 'team_saves', 'away_goalkeeper_saves': 'opponent_saves',
            'home_attempted_passes': 'team_attempted_passes', 'away_attempted_passes': 'opponent_attempted_passes',
            'home_successful_passes': 'team_successful_passes', 'away_successful_passes': 'opponent_successful_passes',
            'home_formation': 'team_formation', 'away_formation': 'opponent_formation',
            'home_rank': 'team_rank', 'away_rank': 'opponent_rank',
            'home_points': 'team_points', 'away_points': 'opponent_points',
            'home_rank_dif': 'team_rank_dif', 'away_rank_dif': 'opponent_rank_dif',
            'home_points_dif': 'team_points_dif', 'away_points_dif': 'opponent_points_dif',
        }

        df_home = df[shared_cols + list(team_cols.keys())].copy()
        df_home.rename(columns=team_cols, inplace=True)
        df_home['is_home'] = 1
        df_home['team_win'] = (df_home['team_goals'] > df_home['opponent_goals']).astype(int)

        df_away = df[shared_cols + list(team_cols.keys())].copy()
        swap = {k.replace("home", "away") if "home" in k else k.replace("away", "home"): v for k, v in team_cols.items()}
        df_away.rename(columns=swap, inplace=True)
        df_away['is_home'] = 0
        df_away['team_win'] = (df_away['team_goals'] > df_away['opponent_goals']).astype(int)

        return pd.concat([df_home, df_away], ignore_index=True)

    def compute_recent_form(self, df, n_matches=5):
        recent_wins, recent_draws, recent_losses = [], [], []
        for idx, row in df.iterrows():
            team_id = row['team']
            past = df.loc[:idx-1]
            team_data = past[past['team'] == team_id].tail(n_matches)
            wins = team_data['team_win'].eq(1).sum()
            draws = team_data['team_win'].eq(0.5).sum()
            losses = team_data['team_win'].eq(0).sum()
            recent_wins.append(wins)
            recent_draws.append(draws)
            recent_losses.append(losses)
        df['recent_wins'] = recent_wins
        df['recent_draws'] = recent_draws
        df['recent_losses'] = recent_losses
        return df

    def load_and_process(self, path):
        df = pd.read_csv(path)

        df['home_rank_dif'] = df['home_rank'] - df['away_rank']
        df['away_rank_dif'] = -df['home_rank_dif']
        df['home_points_dif'] = df['home_points'] - df['away_points']
        df['away_points_dif'] = -df['home_points_dif']

        df_team = self.convert_to_team_level_live(df)

        fill_zero = [
            'team_red_cards', 'team_yellow_cards', 'team_saves',
            'opponent_red_cards', 'opponent_yellow_cards', 'opponent_saves',
            'team_offsides', 'opponent_offsides',
            'team_attempted_passes', 'opponent_attempted_passes'
        ]
        for col in fill_zero:
            df_team[col] = df_team[col].fillna(0)

        for col in ['team_possession', 'opponent_possession']:
            df_team[col] = df_team[col].astype(str).str.replace('%', '', regex=False).astype(float)

        df_team['team_pass_accuracy'] = (df_team['team_successful_passes'] / df_team['team_attempted_passes']).fillna(0)
        df_team['opponent_pass_accuracy'] = (df_team['opponent_successful_passes'] / df_team['opponent_attempted_passes']).fillna(0)
        df_team.drop(columns=['team_successful_passes', 'opponent_successful_passes'], inplace=True)

        df_team['team'] = self.le_team.fit_transform(df_team['team'])
        df_team['opponent'] = self.le_opp.fit_transform(df_team['opponent'])
        df_team['team_formation'] = self.le_form_team.fit_transform(df_team['team_formation'])
        df_team['opponent_formation'] = self.le_form_opp.fit_transform(df_team['opponent_formation'])

        joblib.dump(self.le_team, "models/le_team.pkl")
        joblib.dump(self.le_opp, "models/le_opp.pkl")
        joblib.dump(self.le_form_team, "models/le_form_team.pkl")
        joblib.dump(self.le_form_opp, "models/le_form_opp.pkl")

        df_team['team_form_win_rate'] = df_team.groupby('team_formation')['team_win'].transform('mean')
        df_team['opponent_form_win_rate'] = 1 - df_team.groupby('opponent_formation')['team_win'].transform('mean')

        df_team = self.compute_recent_form(df_team)
        df_team = df_team[df_team["fixture_id"] != 1208324]

        numeric = [col for col in df_team.columns if df_team[col].dtype in [np.float64, np.int64]]
        df_team[numeric] = self.scaler.fit_transform(df_team[numeric])
        joblib.dump(self.scaler, "models/scaler.pkl")

        return df_team



class FatigueProcessor:
    def __init__(self):
        pass

    def load_and_process(self, path):
        df = pd.read_csv(path)

        cols_to_drop = [
            'player_photo', 'offsides', 'goals_conceded', 'goals_saves',
            'dribbles_past', 'penalty_won', 'penalty_committed', 'penalty_saved'
        ]
        df.drop(columns=cols_to_drop, inplace=True, errors='ignore')

        cols_fill_zero = [
            'games_minutes', 'games_rating', 'shots_total', 'shots_on',
            'goals_total', 'goals_assists', 'passes_total', 'passes_key',
            'passes_accuracy', 'tackles_total', 'tackles_blocks',
            'tackles_interceptions', 'duels_total', 'duels_won',
            'dribbles_attempts', 'dribbles_success', 'fouls_drawn', 'fouls_committed'
        ]
        df[cols_fill_zero] = df[cols_fill_zero].fillna(0)
        df = df.dropna(subset=['games_number'])
        df['games_rating'] = pd.to_numeric(df['games_rating'], errors='coerce')
        df['passes_accuracy'] = df['passes_accuracy'].astype(str).str.replace('%', '', regex=False).astype(float) / 100

        df['minutes'] = df['games_minutes'].replace(0, 1)
        df['passes_per_min'] = df['passes_total'] / df['minutes']
        df['duels_per_min'] = df['duels_total'] / df['minutes']
        df['dribbles_per_min'] = df['dribbles_attempts'] / df['minutes']
        df['fouls_per_min'] = df['fouls_committed'] / df['minutes']
        df['dribbles_success_rate'] = df['dribbles_success'] / (df['dribbles_attempts'] + 1e-5)
        df['duels_win_rate'] = df['duels_won'] / (df['duels_total'] + 1e-5)
        df['contribution_rate'] = (df['goals_total'] + df['goals_assists']) / df['minutes']
        df['shot_accuracy'] = df['shots_on'] / (df['shots_total'] + 1e-5)
        df['defensive_actions_per_min'] = (
            df['tackles_total'] + df['tackles_blocks'] + df['tackles_interceptions']) / df['minutes']
        df['duels_balance'] = df['duels_total'] - df['duels_won']
        df['pass_influence'] = df['passes_key'] / (df['passes_total'] + 1e-5)
        df['dribble_pressure'] = df['dribbles_success'] / (df['duels_total'] + 1e-5)
        df['discipline_score'] = (df['cards_yellow'] + 2 * df['cards_red']) / df['minutes']

        if 'games_position' in df.columns:
            df['position'] = LabelEncoder().fit_transform(df['games_position'])

        df = df.sort_values(by=['player_id', 'fixture_id'])
        rolling_features = [
            'games_minutes', 'shots_total', 'shots_on', 'goals_total', 'goals_assists',
            'passes_total', 'passes_key', 'passes_accuracy', 'tackles_total',
            'tackles_blocks', 'tackles_interceptions', 'duels_total', 'duels_won',
            'dribbles_attempts', 'dribbles_success', 'fouls_drawn', 'fouls_committed',
            'cards_yellow', 'cards_red'
        ]
        for col in rolling_features:
            df[f'{col}_avg5'] = df.groupby('player_id')[col].shift(1).rolling(window=5, min_periods=1).mean()
        df = df.dropna(subset=[f'{col}_avg5' for col in rolling_features])

        df['passes_drop_ratio'] = df['passes_total'] / (df['passes_total_avg5'] + 1e-5)
        df['duels_drop_ratio'] = df['duels_total'] / (df['duels_total_avg5'] + 1e-5)
        df['accuracy_drop_ratio'] = df['passes_accuracy'] / (df['passes_accuracy_avg5'] + 1e-5)
        df['passes_trend'] = df.groupby('player_id')['passes_total'].transform(lambda x: x.rolling(3, min_periods=1).apply(lambda s: s.iloc[-1] - s.iloc[0]))
        df['duels_trend'] = df.groupby('player_id')['duels_total'].transform(lambda x: x.rolling(3, min_periods=1).apply(lambda s: s.iloc[-1] - s.iloc[0]))
        df['accuracy_trend'] = df.groupby('player_id')['passes_accuracy'].transform(lambda x: x.rolling(3, min_periods=1).apply(lambda s: s.iloc[-1] - s.iloc[0]))

        df['fatigue_score'] = (
            (df['passes_drop_ratio'] < 0.6).astype(int) +
            (df['duels_drop_ratio'] < 0.6).astype(int) +
            (df['accuracy_drop_ratio'] < 0.8).astype(int)
        )

        group_avg = df.groupby('position')[['passes_per_min', 'duels_per_min', 'passes_accuracy']].transform('mean')
        df['passes_vs_group'] = df['passes_per_min'] / (group_avg['passes_per_min'] + 1e-5)
        df['duels_vs_group'] = df['duels_per_min'] / (group_avg['duels_per_min'] + 1e-5)
        df['accuracy_vs_group'] = df['passes_accuracy'] / (group_avg['passes_accuracy'] + 1e-5)

        df['group_fatigue_score'] = (
            (df['passes_vs_group'] < 0.6).astype(int) +
            (df['duels_vs_group'] < 0.6).astype(int) +
            (df['accuracy_vs_group'] < 0.8).astype(int)
        )
        df['is_fatigued'] = ((df['fatigue_score'] + df['group_fatigue_score']) >= 3).astype(int)

        cols_to_remove = [
            'minutes', 'fatigue_score', 'passes_accuracy_avg5', 'accuracy_vs_group',
            'duels_total_avg5', 'duels_per_min', 'passes_per_min',
            'dribbles_attempts_avg5', 'dribbles_attempts'
        ]
        df.drop(columns=[col for col in cols_to_remove if col in df.columns], inplace=True)

        features = [col for col in df.columns if col.endswith('_avg5')]
        features += [
            'passes_drop_ratio', 'duels_drop_ratio', 'accuracy_drop_ratio',
            'passes_trend', 'duels_trend', 'accuracy_trend', 'passes_accuracy'
        ]
        if 'position' in df.columns:
            features.append('position')

        return df[features + ['is_fatigued']]
