# Predicting Restaurant Success with Demographic Data in Downtown Toronto

The intuition I had is that the type of people that live around a specific restaurant will greatly affect its success. For example, if a restaurant does well in one location, it might do terrible in another despite offering the same service and quality. A potential reason for this is that type of food simply doesn't fit the region's demographic.

What I wanted from this project is to be able to predict the probability of a restaurant succeeding in nearly every neighbourhood. This tool can be used by potential investors or business owners when conducting their market research. To examine this, I collected data from two sources: Yelp's public dataset, and an API from Statistics Canada that offered census data on every FSA value (first three characters of a postal code).

The project consists of four jupyter notebooks with detailed comments and explanations. They are in the following order:

#### Restaurant_Data_Cleaning.ipynb
- Filtering and cleaning Yelp public dataset. Feature engineering and some EDA.
- Outputs a csv file: `cleaned_rest_data.csv`
#### Demographic_Data_Cleaning.ipynb
- Extracting JSON data from Statistics Canada API. Filtering and cleaning, and some feature engineering and EDA.
- Outputs a csv file: `cleaned_demographic_data.csv`
#### Modelling_Data_Cleaning.ipynb
- Inputs both `cleaned_rest_data.csv` and `cleaned_demographic_data.csv`
- Combining both cleaned csv data files, some feature engineering, and getting data ready for modelling
- Outputs a csv file: `model_data.csv`
#### Modelling.ipynb
- Notebook that highlights some of the models that I fitted. Contains hyper-parameter optimizations.


 
  


### Coming soon:
- Dashboard for model predictions
