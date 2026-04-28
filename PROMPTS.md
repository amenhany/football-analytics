# Football Analytics Project - Comprehensive Prompts

## Project Overview Prompt

```
Create a comprehensive football analytics big data analysis project that predicts player market values using machine learning algorithms. The project should:

1. Use Jupyter notebooks for analysis and implementation
2. Predict market values with reasonable accuracy (minimal gaps between predicted and actual values)
3. Implement multiple ML algorithms for robust predictions
4. Use existing football performance data including goals, assists, tackles, passing accuracy, age, position, and tactical role scores
5. Apply constraints to ensure predictions are realistic and reasonable
6. Provide comprehensive visualization and analysis of results
```

## Data Analysis Prompt

```
Analyze the football player dataset to identify key features that influence market value. The analysis should include:

1. Exploratory data analysis of player performance metrics
2. Correlation analysis between performance indicators and market values
3. Feature engineering to create meaningful predictive variables
4. Data preprocessing including handling missing values and outliers
5. Statistical analysis to identify the most important factors for market value prediction

Focus on metrics like:
- Goals and assists per 90 minutes
- Defensive actions (tackles, interceptions)
- Passing accuracy and key passes
- Age and experience factors
- Tactical role suitability scores
- Advanced metrics (xG, xA)
```

## Machine Learning Implementation Prompt

```
Implement machine learning models for football market value prediction with the following requirements:

1. Use multiple algorithms (Random Forest, Gradient Boosting, Ridge, Lasso, Elastic Net)
2. Apply proper train-test splitting and cross-validation
3. Use log transformation for market values to handle skewness
4. Implement feature scaling for optimal performance
5. Apply constraints to ensure reasonable predictions:
   - Maximum 30% increase from original values
   - Minimum values based on age and potential
   - Realistic bounds for different player categories

6. Evaluate models using:
   - Mean Absolute Error (MAE)
   - Root Mean Square Error (RMSE)
   - R-squared (R²)
   - Percentage error analysis

7. Select the best performing model and provide feature importance analysis
```

## Visualization and Reporting Prompt

```
Create comprehensive visualizations to analyze and present the market value prediction results:

1. Predictions vs Actual Values scatter plot with log scale
2. Residual plots to identify prediction patterns
3. Error distribution histograms
4. Feature importance charts for model interpretability
5. Performance comparison across different value ranges
6. Error analysis by player position and age groups

Include detailed markdown explanations for:
- Model selection rationale
- Feature engineering decisions
- Constraint application logic
- Performance interpretation
- Limitations and potential improvements
```

## Code Structure Prompt

```
Structure the Jupyter notebook with clear sections:

1. Import and Setup
   - All required libraries
   - Configuration settings
   - Visualization styling

2. Data Loading and Preprocessing
   - Load master dataset
   - Handle missing values
   - Remove outliers
   - Apply log transformation

3. Feature Engineering
   - Create efficiency metrics
   - Age-related features
   - Experience scores
   - Combined performance indicators

4. Model Preparation
   - Feature selection
   - Data scaling
   - Train-test split

5. Model Training and Evaluation
   - Multiple algorithm implementation
   - Performance metrics calculation
   - Best model selection

6. Prediction with Constraints
   - Apply realistic constraints
   - Final performance evaluation

7. Visualization and Analysis
   - Comprehensive plots
   - Error analysis
   - Feature importance

8. Model Saving and Documentation
   - Save trained model
   - Export feature importance
   - Usage instructions
```

## Reasonable Prediction Constraints Prompt

```
Implement realistic constraints for market value predictions to ensure reasonable outputs:

1. Maximum Increase Constraint:
   - Limit predictions to maximum 30% increase from current market value
   - Prevent unrealistic overvaluation

2. Minimum Value Constraints:
   - Young players (<23 years): minimum 20% above current value (potential)
   - Prime age players (24-28): minimum 80% of current value
   - Older players (>29): minimum 60% of current value

3. Position-Based Adjustments:
   - Strikers and attacking midfielders may have higher valuations
   - Defenders and goalkeepers may have more conservative valuations
   - Consider tactical role suitability scores

4. Performance-Based Floors:
   - High-performing players should not be undervalued
   - Consider recent form and key metrics
   - Factor in team performance and league quality
```

## Usage Instructions Prompt

```
Create clear instructions for using the market value prediction system:

1. Model Loading:
   - How to load the saved model components
   - Required dependencies and versions

2. Data Preparation:
   - Required feature columns
   - Data format specifications
   - Missing value handling

3. Prediction Process:
   - Function usage examples
   - Input data requirements
   - Output interpretation

4. Integration:
   - How to integrate with existing football analytics pipeline
   - Batch prediction capabilities
   - Real-time prediction considerations

5. Maintenance:
   - Model retraining schedule
   - Feature update procedures
   - Performance monitoring
```

## Project Documentation Prompt

```
Create comprehensive project documentation including:

1. Executive Summary:
   - Project objectives and achievements
   - Model performance highlights
   - Business value and applications

2. Technical Documentation:
   - Architecture overview
   - Data flow diagram
   - Model specifications
   - API documentation

3. User Guide:
   - Step-by-step usage instructions
   - Common troubleshooting
   - Best practices
   - Example use cases

4. Development Guide:
   - Code structure explanation
   - Contribution guidelines
   - Testing procedures
   - Deployment instructions

5. Performance Analysis:
   - Model accuracy metrics
   - Computational efficiency
   - Scalability considerations
   - Limitations and future improvements
```

## Where to Write the Code

```
File Structure for Implementation:

1. Main Analysis Notebook:
   📁 notebooks/
   📄 05_market_value_prediction.ipynb
   (This is where the complete market value prediction code should be written)

2. Data Location:
   📁 data/clean/
   📄 master_player_ranking.csv
   (Main dataset with all player metrics and market values)

3. Model Storage:
   📁 models/
   📄 market_value_predictor.pkl
   (Trained model will be saved here)

4. Supporting Scripts:
   📁 scripts/
   (Any utility functions for data processing)

5. Documentation:
   📄 PROMPTS.md
   (This file with all project prompts)

Instructions:
- Open the Jupyter notebook: notebooks/05_market_value_prediction.ipynb
- Run cells sequentially to execute the complete analysis
- The notebook contains all necessary code for data preprocessing, feature engineering, model training, and prediction
- Results will be saved automatically to the models directory
```

## Key Success Metrics

```
Project Success Criteria:

1. Prediction Accuracy:
   - Average percentage error < 25%
   - MAE reasonable relative to market value ranges
   - R² > 0.7 for good model fit

2. Reasonable Constraints:
   - No predictions exceeding 30% increase from current values
   - Minimum value constraints properly applied
   - Realistic valuation patterns across player categories

3. Model Robustness:
   - Consistent performance across different player segments
   - Stable feature importance rankings
   - Good generalization to new data

4. Usability:
   - Clear documentation and instructions
   - Easy-to-use prediction functions
   - Proper model saving and loading capabilities

5. Analysis Quality:
   - Comprehensive exploratory analysis
   - Meaningful feature engineering
   - Clear visualization of results
   - Insightful interpretation of findings
```
