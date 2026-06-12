from collections import Counter


def explain_prediction(
    similar_incidents
):

    teams = [
        x["team"]
        for x in similar_incidents
    ]

    priorities = [
        x["priority"]
        for x in similar_incidents
    ]

    root_causes = [
        x["root_cause"]
        for x in similar_incidents
    ]

    resolution_times = [
        float(x["resolution_time"])
        for x in similar_incidents
    ]

    team_counter = Counter(teams)

    priority_counter = Counter(
        priorities
    )

    root_counter = Counter(
        root_causes
    )

    return {
        "most_common_team":
            team_counter.most_common(1)[0][0],

        "team_support":
            team_counter.most_common(1)[0][1],

        "most_common_priority":
            priority_counter.most_common(1)[0][0],

        "priority_support":
            priority_counter.most_common(1)[0][1],

        "common_root_cause":
            root_counter.most_common(1)[0][0],

        "avg_resolution_time":
            round(
                sum(resolution_times)
                /
                len(resolution_times),
                2
            )
    }