# truecar_webscraping

It is a project to get car's informations from truecar.com website and insert specific features(listed below) into a database: 
name, year, Style, Exterior Color, Interior Color, MPG, Engine, Drive Type, Fuel Type, Transmission, price

For some car items, one or more of the above features are not exist and it is checked in the code.

Considering this fact that duplicate car information might be inserted into the database, drop_duplicates function controls this issue.

The next step can be an ML task: train a machine learning model using the car's informations and predict a new car's price based on them.
