outfield_config = {
    # CENTRE BACK
    "Centre-Back": {
        "Positions": ["Centre-Back"],
        "Aerial Stopper": {
            "Aerial Duels Won (Per90)": 0.55,
            "Clearances (Per90)": 0.25,
            "Shots Blocked (Per90)": 0.20,
        },
        "Ball Playing Defender": {
            "Pass Completion Rate": 0.40,
            "Successful Passes (Per90)": 0.30,
            "Key Passes (Per90)": 0.30,
        },
        "Defensive Sweeper": {
            "Interceptions (Per90)": 0.40,
            "Tackles (Per90)": 0.35,
            "Ground Duels Won (Per90)": 0.25,
        },
    },
    #  FULL BACK
    "Full-Back": {
        "Positions": ["Left-Back", "Right-Back"],
        "Wing Back": {
            "Successful Crosses (Per90)": 0.30,
            "Expected Assists (xA) (Per90)": 0.30,
            "Successful Dribbles (Per90)": 0.25,
            "Key Passes (Per90)": 0.15,
        },
        "Inverted Full Back": {
            "Pass Completion Rate": 0.40,
            "Successful Passes (Per90)": 0.25,
            "Ground Duels Won (Per90)": 0.20,
            "Interceptions (Per90)": 0.15,
        },
        "Defensive Full Back": {
            "Tackles (Per90)": 0.40,
            "Interceptions (Per90)": 0.35,
            "Clearances (Per90)": 0.25,
        },
    },
    #  DEFENSIVE MIDFIELD
    "Defensive Midfield": {
        "Positions": ["Defensive Midfield"],
        "Anchor Man": {
            "Interceptions (Per90)": 0.45,
            "Shots Blocked (Per90)": 0.30,
            "Clearances (Per90)": 0.25,
        },
        "Deep Lying Playmaker": {
            "Pass Completion Rate": 0.40,
            "Successful Passes (Per90)": 0.25,
            "Key Passes (Per90)": 0.35,
        },
        "Ball Winning Midfielder": {
            "Tackles (Per90)": 0.50,
            "Ground Duels Won (Per90)": 0.50,
        },
    },
    # CENTRAL MIDFIELD
    "Central Midfield": {
        "Positions": ["Central Midfield"],
        "Mezzala": {
            "Expected Assists (xA) (Per90)": 0.30,
            "Expected Goals (xG) (Per90)": 0.25,
            "Key Passes (Per90)": 0.25,
            "Successful Dribbles (Per90)": 0.20,
        },
        "Ball Winning Midfielder": {
            "Tackles (Per90)": 0.40,
            "Interceptions (Per90)": 0.35,
            "Ground Duels Won (Per90)": 0.25,
        },
    },
    #  ATTACKING MIDFIELD
    "Attacking Midfield": {
        "Positions": ["Attacking Midfield"],
        "Shadow Striker": {
            "Goals Scored (Per90)": 0.40,
            "Expected Goals (xG) (Per90)": 0.35,
            "Shots On Target (Per90)": 0.25,
        },
        "Playmaker": {
            "Key Passes (Per90)": 0.40,
            "Expected Assists (xA) (Per90)": 0.40,
            "Successful Passes (Per90)": 0.20,
        },
    },
    # WINGER
    "Winger": {
        "Positions": ["Left Winger", "Right Winger", "Left Midfield"],
        "Inside Forward": {
            "Expected Goals (xG) (Per90)": 0.35,
            "Goals Scored (Per90)": 0.30,
            "Shots Taken (Per90)": 0.20,
            "Successful Dribbles (Per90)": 0.15,
        },
        "Traditional Winger": {
            "Successful Crosses (Per90)": 0.55,
            "Expected Assists (xA) (Per90)": 0.25,
            "Key Passes (Per90)": 0.20,
        },
    },
    # STRIKER
    "Striker": {
        "Positions": ["Centre-Forward", "Second Striker"],
        "Poacher": {
            "Goals Scored (Per90)": 0.50,
            "Expected Goals (xG) (Per90)": 0.30,
            "Shots On Target (Per90)": 0.20,
        },
        "Target Man": {
            "Aerial Duels Won (Per90)": 0.50,
            "Ground Duels Won (Per90)": 0.30,
            "Shots Taken (Per90)": 0.20,
        },
        "False Nine": {
            "Expected Assists (xA) (Per90)": 0.35,
            "Key Passes (Per90)": 0.35,
            "Successful Passes (Per90)": 0.20,
            "Successful Dribbles (Per90)": 0.10,
        },
    },
}

gk_config = {
    "Goalkeeper": {
        "Positions": ["Goalkeeper"],
        "Shot Stopper": {
            "Save Percentage": 0.55,
            "Saves (Per90)": 0.35,
            "Punches (Per90)": 0.10,
        },
        "Sweeper Keeper": {
            "Interceptions (Per90)": 0.40,
            "Clearances (Per90)": 0.25,
            "Pass Completion Rate": 0.20,
            "Successful Passes (Per90)": 0.15,
        },
    }
}
