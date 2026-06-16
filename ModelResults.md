# Walkthrough: Realistic Synthetic Data Generation & Retraining

We updated the synthetic data generation logic to be noisy, realistic, and representative of real-world support ticket data. The ML models were successfully retrained, showing realistic metrics (rather than perfect 1.00 scores).

## Changes Made

### 1. Data Generation

#### [data_generation.py](file:///d:/TicketingPlatform/data/data_generation.py)
- **Natural Phrase Variation & Entity Ingestion**: Rewrote the description generator (`generate_natural_description`) to construct varied sentences mixing technical descriptions with prefixes, suffixes, and randomized Faker-generated hostnames, IP addresses, emails, and error codes. Added 10% cross-team noun terminology overlap.
- **Routing Noise**: Added a 7% chance that the primary assigned group (`primary_team`) is misrouted to an incorrect team.
- **Priority Scoring Noise**: Injected normal distribution noise ($\pm 1.5$) to the priority score calculation and simulated a 3% chance of human priority override.
- **Log-normal Resolution Times**: Transitioned from uniform random ranges to log-normal distributions per priority class, introducing a long tail of resolving times and 2% outlier delay spikes.

---

## Retraining & Performance Metrics

The three ML models were retrained using the newly generated data:

### 1. Team Classifier (`train_team.py`)
Achieved a realistic accuracy score of **83%** (down from a perfect, unrealistic 100%):

```text
              precision    recall  f1-score   support

       Batch       0.68      0.73      0.71       301
    Database       0.87      0.85      0.86       726
  Middleware       0.84      0.84      0.84       700
     Network       0.84      0.82      0.83       635
  Unix/Linux       0.85      0.83      0.84       822
      Wintel       0.84      0.86      0.85       816

    accuracy                           0.83      4000
   macro avg       0.82      0.82      0.82      4000
weighted avg       0.83      0.83      0.83      4000
```

### 2. Priority Classifier (`train_priority.py`)
Achieved a realistic accuracy score of **68%** under noisy priority mappings and override conditions:

```text
              precision    recall  f1-score   support

          P1       0.82      0.64      0.72       622
          P2       0.59      0.62      0.61       936
          P3       0.64      0.59      0.61      1277
          P4       0.73      0.86      0.79      1165

    accuracy                           0.68      4000
   macro avg       0.70      0.68      0.68      4000
weighted avg       0.68      0.68      0.68      4000
```

### 3. Resolution Estimator (`train_resolution.py`)
Achieved a realistic resolution duration model fit:
- **Mean Absolute Error (MAE)**: 39.6 minutes
- **$R^2$ Score**: 0.55

---

## Verification Results

We verified that the models compile, load, and run properly using the test suites:
- [test_incident.py](file:///d:/TicketingPlatform/backend/ml/test_incident.py): Successful run:
  ```json
  {"team": "Network", "priority": "P1", "resolution_time": 45.35}
  ```
- [test_team.py](file:///d:/TicketingPlatform/backend/ml/test_team.py): Successfully resolved team classifications.
- [test_priority.py](file:///d:/TicketingPlatform/backend/ml/test_priority.py): Successfully resolved priority classifications.
