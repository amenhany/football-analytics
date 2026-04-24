import pandas as pd
from config import outfield_config, gk_config

def classify_players(df, role_config, hybrid_threshold=5.0):
    all_processed_dfs = []

    for broad_pos, config in role_config.items():
        target_positions = config['Positions']
        role_map = {k: v for k, v in config.items() if k != 'Positions'}

        pos_df = df[df['Position'].isin(target_positions)].copy()
        if len(pos_df) == 0:
            continue

        all_features = set(
            feature for features in role_map.values() for feature in features.keys()
        )

        # ── Step 1: Percentile rank each feature 
        for feature in all_features:
            if feature in pos_df.columns:
                median_val = pos_df[feature].median()
                pos_df[f'{feature}_Pct'] = (
                    pos_df[feature]
                    .fillna(median_val)
                    .rank(pct=True)
                    .clip(0, 1)
                )
            else:
                pos_df[f'{feature}_Pct'] = 0.5

        # ── Step 2: Weighted score per role
        for role, features in role_map.items():
            pct_cols = [f'{feature}_Pct' for feature in features.keys()]
            weights  = list(features.values())

            # Verify weights sum to ~1.0
            weight_sum = sum(weights)
            norm_weights = [w / weight_sum for w in weights]  # normalize just in case

            pos_df[f'{role}_Score'] = (
                pos_df[pct_cols]
                .mul(norm_weights, axis=1)
                .sum(axis=1)
                * 100
            )

        # ── Step 3: Assign best role with hybrid detection
        score_cols = [f'{role}_Score' for role in role_map.keys()]

        def assign_best_role(row):
            scores = {role: row[f'{role}_Score'] for role in role_map.keys()}
            sorted_scores = sorted(scores.values(), reverse=True)
            best_role = max(scores, key=scores.get)

            # If top two scores are within threshold → Hybrid
            if len(sorted_scores) >= 2:
                gap = sorted_scores[0] - sorted_scores[1]
                if gap < hybrid_threshold:
                    return 'Hybrid / Unclear'

            return best_role

        pos_df['Tactical_Role'] = pos_df.apply(assign_best_role, axis=1)
        pos_df['Broad_Position'] = broad_pos

        # ── Step 4: Drop helper columns
        pct_cols_to_drop = [c for c in pos_df.columns if c.endswith('_Pct')]
        pos_df.drop(columns=pct_cols_to_drop, inplace=True)

        all_processed_dfs.append(pos_df)

    result = pd.concat(all_processed_dfs, ignore_index=True)

    # ── Reorder columns cleanly
    score_cols = [c for c in result.columns if c.endswith('_Score')]
    meta_cols  = ['Broad_Position', 'Position', 'Tactical_Role']
    other_cols = [c for c in result.columns if c not in score_cols and c not in meta_cols]

    final_col_order = other_cols + meta_cols + score_cols
    return result[[c for c in final_col_order if c in result.columns]]

