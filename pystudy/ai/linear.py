#!/usr/bin/python3
#_*_encoding:utf-8_*_

import numpy as np
from sklearn.linear_model import LinearRegression

if __name__ == '__main__':
    
    x = np.array([1, 2, 3, 4, 5]).reshape((-1, 1))
    y = np.array([1, 4, 7, 10, 13])

    model = LinearRegression().fit(x, y)
    model_coefficient = model.score(x, y)
    print(model_coefficient)
    
    print('intercept:', model.intercept_)
    print('slope:', model.coef_)

    pred = model.predict(x)
    print(pred)
 
    
