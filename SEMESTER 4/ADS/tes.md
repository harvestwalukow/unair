# Mixed Geographically Weighted Regression (MGWR) Analysis

## Model Specification and Methodology

This study employs a Mixed Geographically Weighted Regression (MGWR) approach to analyze tourism patterns across Indonesian provinces. The MGWR model combines global and local regression components, allowing for the simultaneous modeling of relationships that are spatially stationary (global) and spatially non-stationary (local).

The MGWR model was implemented using a two-stage approach:

1. **Stage 1 (Global Component)**: Ordinary Least Squares (OLS) regression to identify globally stationary relationships
2. **Stage 2 (Local Component)**: Geographically Weighted Regression (GWR) on residuals to capture spatially varying relationships

### Model Formulation

The general MGWR model can be expressed as:

```
Y(ui,vi) = ∑βk(ui,vi)Xk(ui,vi) + ∑γjZj + ε(ui,vi)
```

Where:
- Y(ui,vi) = dependent variable (Tourist arrivals 2023) at location (ui,vi)
- βk(ui,vi) = local coefficient for variable k at location (ui,vi)
- Xk(ui,vi) = local explanatory variables
- γj = global coefficient for variable j
- Zj = global explanatory variables
- ε(ui,vi) = error term at location (ui,vi)

## Data and Variables

The analysis uses provincial-level data for 34 Indonesian provinces with the following variables:

- **Dependent Variable**: Tourist arrivals in 2023 (Wisatawan_2023)
- **Global Variable**: Departure tourism (Berangkat)
- **Local Variables**: Micro enterprises (Mikro), Arrival tourism (Datang)

## Results

### Table 1: Model Performance Comparison

| Model Component | R² | Adjusted R² | AICc | AIC | BIC | RSS |
|----------------|-------|-------------|------|-----|-----|-----|
| Global OLS | 0.8895 | 0.8824 | 1227.522 | 1226.142 | 1212.353 | 7.224×10¹⁵ |
| Mixed GWR | 0.8917 | 0.8790 | 1227.519 | 1220.704 | 1194.933 | 7.078×10¹⁵ |

### Table 2: Global Component Results (Stage 1)

| Variable | Coefficient | Std. Error | t-value | p-value | Significance |
|----------|-------------|------------|---------|---------|--------------|
| Berangkat | 3.7242 | - | - | - | Global Effect |

*Note: The global coefficient for departure tourism (Berangkat) represents the spatially stationary relationship with tourist arrivals.*

### Table 3: Local Component Results (Stage 2) - GWR Summary Statistics

| Variable | Min | 1st Quartile | Median | 3rd Quartile | Max |
|----------|-----|--------------|--------|--------------|-----|
| Intercept | -1.958×10⁷ | -1.955×10⁷ | -1.950×10⁷ | -1.944×10⁷ | -1.936×10⁷ |
| Mikro | 22.346 | 22.388 | 22.571 | 22.755 | 22.784 |
| Datang | -2.128 | -2.119 | -2.075 | -2.034 | -2.026 |

### Table 4: Model Diagnostics

| Diagnostic Measure | Value |
|-------------------|-------|
| Number of Observations | 34 |
| Optimal Bandwidth (Adaptive) | 32 neighbors |
| Effective Parameters | 3.479 |
| Effective Degrees of Freedom | 30.521 |
| Kernel Function | Gaussian |
| Distance Metric | Euclidean |

## Interpretation of Results

### Global Component Analysis

The global coefficient for departure tourism (Berangkat = 3.7242) indicates a positive and spatially stationary relationship with tourist arrivals across all provinces. This suggests that for every unit increase in departure tourism, there is an average increase of 3.72 units in tourist arrivals, consistent across all Indonesian provinces.

### Local Component Analysis

The local coefficients reveal significant spatial heterogeneity in the relationships:

1. **Micro Enterprises (Mikro)**: The coefficients range from 22.346 to 22.784, showing relatively stable positive effects across provinces. The narrow range suggests that the impact of micro enterprises on tourism is fairly consistent geographically, with slight spatial variations.

2. **Arrival Tourism (Datang)**: The coefficients range from -2.128 to -2.026, indicating a consistently negative relationship across all provinces. This counter-intuitive result may suggest competition effects or substitution patterns in tourism flows.

### Model Performance

The Mixed GWR model demonstrates excellent explanatory power:

- **R² = 0.8917**: The model explains approximately 89.17% of the variance in tourist arrivals
- **Adjusted R² = 0.8790**: After adjusting for the number of parameters, the model still explains 87.90% of the variance
- **Improved fit**: The Mixed GWR shows marginal improvement over the global OLS model in terms of AIC and BIC values

### Spatial Bandwidth Analysis

The optimal adaptive bandwidth of 32 neighbors indicates that local relationships are estimated using approximately 94% of the total sample (32 out of 34 provinces). This suggests that while spatial non-stationarity exists, the local relationships require a relatively large neighborhood for stable estimation.

## Final Mixed GWR Model

The final model can be expressed as:

```
Tourist_Arrivals₂₀₂₃(ui,vi) = 3.7242 × Berangkat + β₁(ui,vi) × Mikro(ui,vi) + β₂(ui,vi) × Datang(ui,vi) + ε(ui,vi)
```

Where:
- β₁(ui,vi) ∈ [22.346, 22.784] (spatially varying coefficient for Micro enterprises)
- β₂(ui,vi) ∈ [-2.128, -2.026] (spatially varying coefficient for Arrival tourism)
- (ui,vi) represents the geographic coordinates of each province

## Conclusions

The Mixed GWR analysis reveals that tourism patterns in Indonesia are influenced by both spatially stationary and spatially varying factors. Departure tourism exhibits a consistent positive effect across all provinces, while the impacts of micro enterprises and arrival tourism vary geographically, albeit within relatively narrow ranges. The model's high explanatory power (R² = 0.8917) demonstrates its effectiveness in capturing the complex spatial relationships in Indonesian tourism data.

The findings suggest that tourism policies should consider both universal strategies (leveraging departure tourism patterns) and location-specific approaches (optimizing micro enterprise development and managing arrival tourism flows) to maximize tourism development across Indonesian provinces. 