# MGWR Model Results Summary

## Key Model Performance Metrics

| Metric | Global OLS | Local GWR | Combined MGWR |
|--------|------------|-----------|---------------|
| **R-squared** | 0.0667 | 0.8917 | **0.9584** |
| **Adjusted R-squared** | 0.0376 | 0.8790 | **0.9540** |
| **AICc** | - | 1227.5 | - |
| **Variables** | Berangkat (Global) | Mikro + Datang (Local) | All Combined |

## Coefficient Summary

### Global Effects (Constant Across Space)
| Variable | Coefficient | Interpretation |
|----------|-------------|----------------|
| **Berangkat** | 3.724 | +3.72 tourists per additional passenger departure (not significant, p=0.1402) |

### Local Effects (Spatially Varying)
| Variable | Min | Median | Max | Spatial Variation |
|----------|-----|--------|-----|-------------------|
| **Mikro** | 22.346 | 22.571 | 22.784 | Low (0.65% CV) |
| **Datang** | -2.128 | -2.075 | -2.026 | Moderate (1.64% CV) |

## Model Interpretation

### What the Results Mean:

1. **Excellent Model Fit**: The combined MGWR explains 95.8% of domestic tourism variation across Indonesian provinces

2. **Global Transportation Effect**: Passenger departures show a positive but non-significant relationship (3.72 tourists per departure, p=0.1402), indicating high spatial heterogeneity

3. **Local Micro-Industry Effect**: Micro-scale industry expenditure has consistently positive impact (22.3-22.8 tourists per unit) with minimal spatial variation

4. **Local Arrival Redistribution**: Passenger arrivals show negative local effects (-2.0 to -2.1), suggesting tourism redistribution rather than net growth after accounting for global departure effects

### Policy Recommendations:

- **National Level**: Focus on expanding airport departure capacity
- **Regional Level**: Invest in micro-scale tourism businesses with region-specific strategies
- **Local Level**: Manage arrival patterns to optimize tourism distribution

## Technical Details

- **Bandwidth**: 32 neighbors (adaptive)
- **Kernel**: Gaussian
- **Effective Parameters**: 3.48
- **Sample Size**: 34 Indonesian provinces
- **Dependent Variable**: Domestic tourists in 2023

## Model Equation

```
Domestic_Tourism = 17,900,000 + 3.72 × Departures_Global + 
                   Local_Effects(Micro_Industry + Arrivals) + Error
```

Where Local_Effects vary by geographic location (ui, vi). 