import pandas
import zipfile
import os

data: pandas.DataFrame = pandas.read_csv("/home/kiranftw/COLLEGE/Resume-Screening-ATS-Analytics-using-Generative-AI/amazon.csv")
print(data.head())
print(data.columns)
print(data.shape)
print(data.info())
data["discounted_price"]= data["discounted_price"].str.replace("₹", "").str.replace(",", "").astype(float)

print(data["discounted_price"].dtype)


def datacleaning(dataframe: pandas.DataFrame):
    dataframe = dataframe.str.replace("₹", "").str.replace(",", "").str.replace("%", "").astype(float)
    print(data.head())
    return dataframe

datacleaning(data['discount_percentage'])
print(data["discount_percentage"].dtype)

print(data["discount_percentage"].head())