import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker
import math
fake = Faker()
NUM_ROWS = 20000
APP_TEAM_MAP = {
    "Active Directory": ["Wintel"],
    "DNS Server": ["Wintel"],
    "Windows File Server": ["Wintel"],
    "IIS Server": ["Wintel"],
    "Linux ERP Server": ["Unix/Linux"],
    "Linux Web Server": ["Unix/Linux"],
    "Apache Server": ["Unix/Linux"],
    "NFS Storage": ["Unix/Linux"],
    "VPN Gateway": ["Network"],
    "Firewall": ["Network"],
    "Load Balancer": ["Network"],
    "Oracle DB": ["Database"],
    "SQL Server": ["Database"],
    "PostgreSQL": ["Database"],
    "Tomcat": ["Middleware"],
    "WebSphere": ["Middleware"],
    "Kafka": ["Middleware"],
    "IBM MQ": ["Middleware"],
    "Control-M": ["Batch"],
    "Autosys": ["Batch"]
}

APP_CATEGORY = {
    "Active Directory":"Authentication",
    "DNS Server":"Authentication",
    "Windows File Server":"Windows Infrastructure",
    "IIS Server":"Middleware",
    "Linux ERP Server":"Application",
    "Linux Web Server":"Application",
    "Apache Server":"Middleware",
    "NFS Storage":"Storage",
    "VPN Gateway":"Connectivity",
    "Firewall":"Security",
    "Load Balancer":"Connectivity",
    "Oracle DB":"Database",
    "SQL Server":"Database",
    "PostgreSQL":"Database",
    "Tomcat":"Middleware",
    "WebSphere":"Middleware",
    "Kafka":"Middleware",
    "IBM MQ":"Middleware",
    "Control-M":"Batch Failure",
    "Autosys":"Batch Failure"
}
DESCRIPTIONS = {
    "Wintel":[
        "User account locked",
        "Active Directory authentication failure",
        "DNS server not responding",
        "Group policy update failed",
        "Windows server unreachable"
    ],
    "Unix/Linux":[
        "Linux server unreachable",
        "SSH connection refused",
        "Filesystem utilization exceeded threshold",
        "CPU utilization above 95 percent",
        "Cron job execution failed"
    ],
    "Network":[
        "VPN connection failed",
        "Firewall blocking traffic",
        "Packet loss detected",
        "Load balancer health check failed",
        "Network latency exceeds threshold"
    ],
    "Database":[
        "Database timeout detected",
        "Oracle listener unavailable",
        "Database lock detected",
        "Connection pool exhausted",
        "Slow query execution observed"
    ],
    "Middleware":[
        "Tomcat service unavailable",
        "Kafka consumer lag detected",
        "Message queue processing delayed",
        "Application deployment failed",
        "WebSphere JVM memory exhausted"
    ],
    "Batch":[
        "Control-M job failed",
        "Batch process terminated unexpectedly",
        "Payroll batch execution failed",
        "ETL job timeout detected",
        "Autosys scheduler unavailable"
    ]
}
ROOT_CAUSES = {
    "Wintel":["Active Directory Failure","Account Lockout","DNS Service Failure"],
    "Unix/Linux":["Filesystem Full","Memory Exhaustion","CPU Saturation","Kernel Panic"],
    "Network":["VPN Tunnel Failure","Firewall Misconfiguration","Network Congestion"],
    "Database":["Database Lock","Slow Query Execution","Listener Failure"],
    "Middleware":["Middleware Service Down","Thread Pool Exhaustion","Message Queue Failure"],
    "Batch":["Scheduler Failure","ETL Failure","Batch Timeout"]
}
SCOPE_MODIFIERS = {
    "single_user": [
        "reported by a single user",
        "affecting one employee",
        "isolated issue observed"
    ],

    "department": [
        "affecting multiple users",
        "reported by a department",
        "impacting a business team"
    ],

    "site": [
        "impacting an office location",
        "affecting a large user group",
        "reported across a site"
    ],
    "enterprise": [
        "impacting business operations",
        "affecting users across the enterprise",
        "reported organization wide"
    ]
}
TEAM_MULTIPLIER = {
    "Wintel":1.0,
    "Unix/Linux":1.1,
    "Network":1.0,
    "Database":1.3,
    "Middleware":1.2,
    "Batch":0.9
}
APP_CRITICALITY = {
    "Active Directory": 8,
    "DNS Server": 7,
    "Windows File Server": 6,
    "IIS Server": 7,

    "Linux ERP Server": 9,
    "Linux Web Server": 7,
    "Apache Server": 7,
    "NFS Storage": 6,

    "VPN Gateway": 9,
    "Firewall": 9,
    "Load Balancer": 8,

    "Oracle DB": 10,
    "SQL Server": 10,
    "PostgreSQL": 9,

    "Tomcat": 8,
    "WebSphere": 9,
    "Kafka": 8,
    "IBM MQ": 8,

    "Control-M": 8,
    "Autosys": 7
}
SCOPE_WEIGHTS = {
    "single_user": 40,
    "department": 30,
    "site": 20,
    "enterprise": 10
}
APP_WEIGHTS = {
    "Active Directory": 8,
    "DNS Server": 4,
    "Windows File Server": 5,
    "IIS Server": 4,

    "Linux ERP Server": 8,
    "Linux Web Server": 6,
    "Apache Server": 5,
    "NFS Storage": 3,

    "VPN Gateway": 8,
    "Firewall": 4,
    "Load Balancer": 4,

    "Oracle DB": 8,
    "SQL Server": 7,
    "PostgreSQL": 4,

    "Tomcat": 6,
    "WebSphere": 5,
    "Kafka": 4,
    "IBM MQ": 3,

    "Control-M": 4,
    "Autosys": 3
}
def choose_scope():
    return random.choices(
        list(SCOPE_WEIGHTS.keys()),
        weights=list(SCOPE_WEIGHTS.values())
    )[0]

def generate_users(scope):
    if scope == "single_user":
        return random.randint(1,10)
    elif scope == "department":
        return random.randint(20,100)
    elif scope == "site":
        return random.randint(100,1000)
    else:
        return random.randint(1000,10000)

def generate_natural_description(primary_team, app, scope):
    # 90% probability of selecting true team's description base, 10% from another team (vocabulary overlap)
    if random.random() < 0.90:
        base_desc = random.choice(DESCRIPTIONS[primary_team])
    else:
        other_team = random.choice([t for t in DESCRIPTIONS.keys() if t != primary_team])
        base_desc = random.choice(DESCRIPTIONS[other_team])
    
    prefixes = [
        "Alert: ", "Incident report: ", "URGENT - ", "System status update - ", 
        "Notification: ", "Error reported: ", "Monitoring alert: ", "Issue detected: ", ""
    ]
    suffixes = [
        "immediately", "please investigate", "asap", "blocking work", 
        "needs attention", "during routine check", "causing service disruption", ""
    ]
    
    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    
    desc_str = f"{prefix}{base_desc}"
    if suffix:
        desc_str = f"{desc_str} {suffix}"
        
    # Inject Faker entities for realistic noise (e.g. hostnames, IP, email, errors)
    entities = []
    if random.random() < 0.4:
        entities.append(f"on server {fake.hostname()}")
    if random.random() < 0.3:
        entities.append(f"IP {fake.ipv4()}")
    if random.random() < 0.2:
        entities.append(f"impacted email {fake.email()}")
    if random.random() < 0.25:
        entities.append(f"code: ERR-{random.randint(100, 999)}")
        
    if entities:
        desc_str = f"{desc_str} ({', '.join(entities)})"
        
    scope_text = random.choice(SCOPE_MODIFIERS[scope])
    
    # Randomize ordering of core issue details and scope impact text
    if random.random() < 0.5:
        final_desc = f"{desc_str}. This is {scope_text}."
    else:
        final_desc = f"Report shows issue is {scope_text}. Details: {desc_str}."
        
    return final_desc

def generate_priority(app, users):
    criticality = APP_CRITICALITY[app]
    # Add normal distribution noise to score to simulate realistic grading variability
    noise = random.normalvariate(0, 1.5)
    score = criticality + (math.log10(users) * 4) + noise

    if score >= 20:
        priority = "P1"
    elif score >= 16:
        priority = "P2"
    elif score >= 12:
        priority = "P3"
    else:
        priority = "P4"

    # 3% chance of human priority override / grading error
    if random.random() < 0.03:
        p_levels = ["P1", "P2", "P3", "P4"]
        idx = p_levels.index(priority)
        shift = random.choice([-1, 1])
        if 0 <= idx + shift < len(p_levels):
            priority = p_levels[idx + shift]

    return priority

def resolution_time(priority, teams):
    # Log-normal distribution parameters (mu, sigma) to simulate real resolution times
    # Median values: P1: ~35m, P2: ~150m, P3: ~240m, P4: ~35m
    params = {
        "P1": (3.55, 0.4),
        "P2": (5.01, 0.2),
        "P3": (5.48, 0.2),
        "P4": (3.55, 0.4)
    }
    mu, sigma = params[priority]
    base = random.lognormvariate(mu, sigma)
    
    mult = sum(TEAM_MULTIPLIER[t] for t in teams) / len(teams)
    time_val = base * mult
    
    # 2% chance of a major system outlier / delayed restoration
    if random.random() < 0.02:
        time_val *= random.uniform(3.0, 5.0)
        
    return max(5, int(time_val))

rows = []
start_date = datetime(2025, 1, 1)
end_date = datetime(2026, 6, 30)
apps = list(APP_WEIGHTS.keys())
app_weights = list(APP_WEIGHTS.values())

for ticket_id in range(1, NUM_ROWS + 1):
    app = random.choices(
        apps,
        weights=app_weights
    )[0]

    scope = choose_scope()
    users = generate_users(scope)

    # 1. Determine underlying correct assignment group
    true_team = random.choice(APP_TEAM_MAP[app])

    # 2. Generate natural description from the true team's issues
    desc = generate_natural_description(true_team, app, scope)

    # 3. Simulate routing noise (7% chance of initial assignment error to a wrong group)
    if random.random() < 0.07:
        all_teams_list = ["Wintel", "Unix/Linux", "Network", "Database", "Middleware", "Batch"]
        primary_team = random.choice([t for t in all_teams_list if t != true_team])
    else:
        primary_team = true_team

    # 4. Construct comma-separated teams list starting with primary_team
    teams = [primary_team]
    r = random.random()
    if r < 0.25:
        extras = [x for x in ["Wintel", "Unix/Linux", "Network", "Database", "Middleware", "Batch"]
                  if x != primary_team]
        teams.append(random.choice(extras))
    elif r < 0.30:
        extras = [x for x in ["Wintel", "Unix/Linux", "Network", "Database", "Middleware", "Batch"]
                  if x != primary_team]
        teams.extend(random.sample(extras, 2))

    priority = generate_priority(app, users)
    res_time = resolution_time(priority, teams)
    category = APP_CATEGORY[app]

    environment = random.choices(
        ["Production", "UAT", "Development"],
        weights=[70, 20, 10]
    )[0]

    status = random.choices(
        ["Resolved", "Closed", "Cancelled"],
        weights=[80, 15, 5]
    )[0]

    # Set root cause based on the true underlying team issue
    root_cause = random.choice(ROOT_CAUSES[true_team])

    created_at = fake.date_time_between(
        start_date=start_date,
        end_date=end_date
    )

    resolved_at = created_at + timedelta(minutes=res_time)

    rows.append({
        "ticket_id": ticket_id,
        "description": desc,
        "teams": ",".join(teams),
        "priority": priority,
        "resolution_time": res_time,
        "application": app,
        "environment": environment,
        "category": category,
        "status": status,
        "affected_users": users,
        "impact_scope": scope,
        "created_at": created_at,
        "resolved_at": resolved_at,
        "root_cause": root_cause
    })

df = pd.DataFrame(rows)
df.to_csv("synthetic_tickets.csv", index=False)