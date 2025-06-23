# prompts.py

SPORT_OPTIONS = {
    "Football": {
        "Roles": ["Striker", "Winger", "Attacking Midfielder", "Defender", "Goalkeeper"],
        "Skills": {
            "Striker": ["Finishing", "Positioning", "Off-the-ball runs"],
            "Winger": ["Dribbling", "Crossing", "Cutting inside"],
            "Attacking Midfielder": ["Through balls", "Creative passing"],
            "Defender": ["1-on-1 defending", "Interceptions", "Heading"],
            "Goalkeeper": ["Shot-stopping", "Distribution", "Positioning"]
        }
    },
    "Cricket": {
        "Disciplines": ["Batting", "Bowling", "Fielding"],
        "Skills": {
            "Batting": ["Straight drive", "Pull shot", "Hook", "Reverse sweep", "Paddle scoop"],
            "Bowling": ["Pace", "Swing", "Off-spin", "Leg-spin"],
            "Fielding": ["Slip catching", "Ground fielding", "Wicketkeeping"]
        }
    },
    "Rugby": {
        "Positions": ["Forwards", "Backs"],
        "Skills": {
            "Forwards": ["Tackling", "Scrum technique", "Line-out throwing"],
            "Backs": ["Passing accuracy", "Kicking", "Defensive reads"]
        }
    },
    "Tennis": {
        "Aspects": ["Serve", "Groundstroke", "Volley", "Return"],
        "Skills": {
            "Serve": ["Flat serve", "Slice serve", "Kick serve"],
            "Groundstroke": ["Forehand", "Backhand"],
            "Volley": ["Half-volley", "Drop volley"],
            "Return": ["Block return", "Drive return"]
        }
    },
    "Athletics": {
        "Categories": ["Track", "Field", "Combined", "Road & Cross-Country"],
        "Events": {
            "Track": ["100m", "200m", "400m", "Hurdles", "Relay"],
            "Field": ["Long Jump", "High Jump", "Javelin", "Shot Put"],
            "Combined": ["Decathlon", "Heptathlon"],
            "Road & Cross-Country": ["5K", "10K", "Marathon"]
        }
    }
}

DEFAULT_PROMPTS = {
    ("Football", "Striker"): "Analyze my striking mechanics: foot placement at contact, hip rotation, follow-through, and shot placement.",
    ("Football", "Winger"): "Evaluate my dribbling technique and crossing delivery: body lean, plant-foot stability, and ball flight.",
    ("Football", "Goalkeeper"): "Critique my shot-stopping technique: dive initiation, hand position, and recovery to feet.",
    ("Cricket", "Batting"): "Analyze my batting technique: grip, stance, back-lift, footwork to the pitch, and head position.",
    ("Cricket", "Bowling"): "Evaluate my bowling action: run-up rhythm, arm path, release point, and follow-through.",
    ("Athletics", "100m"): "Analyze my starting block exit and drive phase: reaction time, body angle, and transition.",
    ("Athletics", "Shot Put"): "Assess my shot put technique: grip, glide/spin mechanics, release angle, and follow-through.",
    ("Athletics", "Decathlon"): "Critique my transition between events: fatigue management, throws/jumps form, and sprint/hurdles execution.",
}
