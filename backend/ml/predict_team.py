from backend.ml.model_registry import get_model

def predict_team(description: str) -> str:
    try:
        model = get_model("team")
        return model.predict([description])[0]
    except Exception as e:
        print(f"predict_team model load failed, running fallback heuristics: {e}")
        desc = description.lower()
        if any(w in desc for w in ["database", "sql", "oracle", "db", "query", "lock", "postgres"]):
            return "Database"
        elif any(w in desc for w in ["vpn", "network", "router", "switch", "latency", "packet loss", "connectivity", "internet"]):
            return "Network"
        elif any(w in desc for w in ["linux", "unix", "ssh", "host", "redhat", "centos"]):
            return "Unix/Linux"
        elif any(w in desc for w in ["windows", "active directory", "domain", "wintel", "iis"]):
            return "Wintel"
        elif any(w in desc for w in ["middleware", "tomcat", "apache", "weblogic", "mq", "websphere"]):
            return "Middleware"
        elif any(w in desc for w in ["batch", "job", "autosys", "scheduler", "cron", "failed job"]):
            return "Batch"
        return "Unix/Linux"