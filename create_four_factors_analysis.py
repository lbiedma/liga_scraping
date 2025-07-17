import pandas as pd

def create_fgm_fga_columns(df: pd.DataFrame) -> pd.DataFrame:
    list_of_cols = ["2p_A/I", "3p_A/I", "ft_A/I"]

    for col in list_of_cols:
        df[f"{col}_FGM"] = df[col].str.split("/").str[0].astype(int)
        df[f"{col}_FGA"] = df[col].str.split("/").str[1].astype(int)
    df["FGA"] = df["2p_A/I_FGA"] + df["3p_A/I_FGA"]
    df["FGM"] = df["2p_A/I_FGM"] + df["3p_A/I_FGM"]
    df["FTA"] = df["ft_A/I_FGA"]
    return df

def create_opp_rebs(df: pd.DataFrame, opp_df: pd.DataFrame) -> pd.DataFrame:
    df["opp_ORB"] = opp_df["Ofe."]
    df["opp_DRB"] = opp_df["Def."]

    return df

def create_four_factors_analysis(df: pd.DataFrame, opp_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a four factors analysis for a given dataframe.
    """
    df = create_fgm_fga_columns(df)
    df = create_opp_rebs(df, opp_df)
    final_stats = df.sum(numeric_only=True)
    final_stats["effective_fg_pct"] = (final_stats["2p_A/I_FGM"] + 1.5 * final_stats["3p_A/I_FGM"]) / (final_stats["2p_A/I_FGA"] + final_stats["3p_A/I_FGA"])
    final_stats["tov_factor"] = final_stats["PÉR"] / (final_stats["FGA"] + 0.44 * final_stats["FTA"] + final_stats["PÉR"])
    final_stats["off_reb_factor"] = final_stats["Ofe."] / (final_stats["Ofe."] + final_stats["opp_DRB"])
    final_stats["ft_factor"] = final_stats["ft_A/I_FGA"] / final_stats["FGA"]
    final_stats["four_off_factors_score"] = 0.4 * final_stats["effective_fg_pct"] + 0.25 * final_stats["tov_factor"] + 0.2 * final_stats["off_reb_factor"] + 0.15 * final_stats["ft_factor"]

    return final_stats
