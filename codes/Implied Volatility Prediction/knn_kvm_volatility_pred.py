import pandas as pd
import numpy as np
import time
from sklearn.preprocessing import MinMaxScaler
from sklearn import neighbors
from sklearn import cross_validation
from sklearn import svm
import matplotlib.pyplot as plt

## Split data into training and test sets (data & labels for each)
## Input Parameters
# data: dataframe
# train_size: training size (between 0 and 1)
## Optional Parameters:
# drop: labels top drop as a list
# scale: if True, scales data to values between 0 and 1
def split_data(data, train_size, drop=[], scale=False):
    data = data.drop(drop, axis=1)
    
    if (scale):
        vals = data.values
        cols = data.columns
        vals_scaled = MinMaxScaler().fit_transform(vals)
        data = pd.DataFrame(vals_scaled, columns=cols)
    
    train_data, test_data = cross_validation.train_test_split(data, train_size=train_size, random_state=42)
    train_data_labels = train_data['Implied Volatility']
    test_data_labels = test_data['Implied Volatility']
    train_data = train_data.drop('Implied Volatility', axis=1)
    test_data = test_data.drop('Implied Volatility', axis=1)
    
    return train_data, train_data_labels, test_data, test_data_labels

## Calculate Mean Squared Error, Mean Error, Max Error, Min Error
def compute_measure(predicted_labels, actual_labels):
    results = []
    err = actual_labels - predicted_labels
    results.append(np.sum(np.power(err, 2)) / len(err)) # Mean Squared Error
    results.append(np.mean(err)) # Mean Error
    results.append(np.median(err)) # Median Error
    results.append(np.max(err)) # Max Error
    results.append(np.min(err)) # Min Error
    
    return results

# Run k Nearest Neighbors Regression and Report Error Measures
def run_kNN_Regression(train_data, train_labels, test_data, test_labels, n_neighbors=5, 
                       weights='uniform', algorithm='kd_tree', metric='minkowski'):
    print('Running {:d}-nearest neighbors using the {:s} algorithm'.format(n_neighbors, algorithm))
    print('Weights - {:s}, Metric - {:s}'.format(weights, metric))
    kNN = neighbors.KNeighborsRegressor(n_neighbors=n_neighbors, weights=weights, algorithm=algorithm, metric=metric)
    kNN.fit(train_data, train_labels)
    predicted_labels = kNN.predict(test_data)
    
    results = compute_measure(predicted_labels, test_labels)
    print('Error - MSE: {:4f}, Mean: {:4f}, Media-n: {:4f}, Max: {:4f}, Min: {:4f}'.format(*results))
    return results

# Run Support Vector Machine Regression and Report Error Measures
def run_SVM_Regression(train_data, train_labels, test_data, test_labels, C=1.0,
                       epsilon=0.1, kernel='rbf', degree=3, gamma='auto', coef0=0.0, 
                       shrinking=True, tol=1e-3, max_iter=-1):
    print('Running SVM regression using the {:s} kernel'.format(kernel))
    print('C - {:f}, epsilon - {:f}, degree - {:d}'.format(C, epsilon, degree))
    print('coef0 - {:f}, shrinking - {:b}, tolerance - {:f}'.format(coef0, shrinking, tol))
    SVM = svm.SVR(C=C, epsilon=epsilon, kernel=kernel, degree=degree, gamma=gamma, 
                  coef0=coef0, shrinking=shrinking, tol=tol, max_iter=max_iter)
    SVM.fit(train_data, train_labels)
    predicted_labels = SVM.predict(test_data)
    
    results = compute_measure(predicted_labels, test_labels)
    print('Error - MSE: {:4f}, Mean: {:4f}, Median: {:4f}, Max: {:4f}, Min: {:4f}'.format(*results))
    return results

# Run k Nearest Neighbors Regression and Report Error Measures
def run_Radius_Regression(train_data, train_labels, test_data, test_labels, radius=1.0,
                          weights='uniform', algorithm='auto', metric='minkowski'):
    print('Running {:f}-radius neighbors using the {:s} algorithm'.format(radius, algorithm))
    print('Weights - {:s}, Metric - {:s}'.format(weights, metric))
    rng = neighbors.RadiusNeighborsRegressor(radius=radius, weights=weights, 
                                             algorithm=algorithm, metric=metric)
    rng.fit(train_data, train_labels)
    predicted_labels = rng.predict(test_data)

    results = compute_measure(predicted_labels, test_labels)
    print('Error - MSE: {:4f}, Mean: {:4f}, Median: {:4f}, Max: {:4f}, Min: {:4f}'.format(*results))
    return results

# Main
df = pd.read_csv('cisc5352.project.1.option_data.csv')
df.drop(['Volatility'], axis=1).describe()
drop = df.columns.difference(['Option_Price', 'Stock_Price', 'Strike_Price', 'Option_Type', 'Implied Volatility'])

## KNN
# Test different algorithms
final_results = []

for algorithm in ['kd_tree', 'ball_tree']:
    for i in range(100):
        results = []
        df_train, df_train_labels, df_test, df_test_labels = split_data(df.sample(n=2000), 0.8, drop=drop, scale=True)
        res = run_kNN_Regression(df_train, df_train_labels, df_test, df_test_labels, algorithm=algorithm)
        print('\n')
        results.append(res)
    final_results.append(results)

# Plot
avg = [[sum(i) / len(i) for i in zip(*x)] for x in final_results]
mses = [x[0] for x in avg]
n = [0, 1]
labels = ['kd-tree', 'ball-tree']
plt.bar(n, mses, align='center')
plt.xlabel('n_neighbors')
plt.ylabel('Mean Squared Error')
plt.xticks(n, labels)
plt.title('Choice of Algorithm - 2000 samples x 100 runs')


# Test different distance metrics
final_results = []

for metric in ['euclidean', 'manhattan', 'chebyshev', 'minkowski']:
    for i in range(100):
        results = []
        df_train, df_train_labels, df_test, df_test_labels = split_data(df.sample(n=2000), 0.8, drop=drop, scale=True)
        res = run_kNN_Regression(df_train, df_train_labels, df_test, df_test_labels, metric=metric)
        print('\n')
        results.append(res)
    final_results.append(results)

# Plot
avg = [[sum(i) / len(i) for i in zip(*x)] for x in final_results]
mses = [x[0] for x in avg]
n = [0, 1, 2, 3]
labels = ['euclidean', 'manhattan', 'chebyshev', 'minkowski']
plt.bar(n, mses, align='center')
plt.xlabel('n_neighbors')
plt.ylabel('Mean Squared Error')
plt.xticks(n, labels)
plt.title('Choice of Metric - 2000 samples x 100 runs')

# Test different n-neighbors
final_results = []

for n in range(5, 36, 5):
    for i in range(100):
        results = []
        df_train, df_train_labels, df_test, df_test_labels = split_data(df.sample(n=2000), 0.8, drop=drop, scale=True)
        res = run_kNN_Regression(df_train, df_train_labels, df_test, df_test_labels, n_neighbors=n)
        print('\n')
        results.append(res)
    final_results.append(results)

# Plot
avg = [[sum(i) / len(i) for i in zip(*x)] for x in final_results]
mses = [x[0] for x in avg]
n = range(5, 36, 5)
plt.plot(n, mses)
plt.xlabel('n_neighbors')
plt.ylabel('Mean Squared Error')
plt.title('Choice of n_neighbors - 2000 samples x 100 runs')
axes = plt.gca()
axes.set_ylim([0.020, 0.035])


# Test different weight types
final_results = []

for weight in ['uniform', 'distance']:
    for i in range(100):
        results = []
        df_train, df_train_labels, df_test, df_test_labels = split_data(df.sample(n=2000), 0.8, drop=drop, scale=True)
        res = run_kNN_Regression(df_train, df_train_labels, df_test, df_test_labels, n_neighbors=30, 
                                 weights=weight)
        print('\n')
        results.append(res)
    final_results.append(results)

# Plot
avg = [[sum(i) / len(i) for i in zip(*x)] for x in final_results]
mses = [x[0] for x in avg]
n = [0, 1]
labels = ['uniform', 'distance']
plt.bar(n, mses, align='center')
plt.xlabel('weights')
plt.ylabel('Mean Squared Error')
plt.xticks(n, labels)
plt.title('Uniform vs Weighted Distance - 2000 samples x 100 runs')
axes = plt.gca()
axes.set_ylim([0.000, 0.035])


# KNN on 2nd dataset - Test n-neighbors again
df2 = pd.read_csv('Quiz5_raw.csv')
drop2 = ['Time_to_Maturity', 'Interest_Rate']

final_results = []

for n in range(5, 36, 5):
    for i in range(100):
        results = []
        df_train, df_train_labels, df_test, df_test_labels = split_data(df2.sample(n=750), 0.8, drop=drop2, scale=True)
        res = run_kNN_Regression(df_train, df_train_labels, df_test, df_test_labels, n_neighbors=n)
        print('\n')
        results.append(res)
    final_results.append(results)

# Plot
avg = [[sum(i) / len(i) for i in zip(*x)] for x in final_results]
mses = [x[0] for x in avg]
n = range(5, 36, 5)
plt.plot(n, mses)
plt.xlabel('n_neighbors')
plt.ylabel('Mean Squared Error')
plt.title('Choice of n_neighbors - 750 samples x 100 runs')
axes = plt.gca()
axes.set_ylim([0.005, 0.030])


## SVM
# Test kernels
final_results = []

for kernel in ['linear', 'poly', 'rbf', 'sigmoid']:
    for i in range(10):
        results = []
        df_train, df_train_labels, df_test, df_test_labels = split_data(df.sample(n=2000), 0.8, drop=drop, scale=True)
        res = run_SVM_Regression(df_train, df_train_labels, df_test, df_test_labels, kernel=kernel)
        print('\n')
        results.append(res)
    final_results.append(results)

# plot
avg = [[sum(i) / len(i) for i in zip(*x)] for x in final_results]
mses = [x[0] for x in avg]
n = [0, 1, 2, 3]
labels = ['linear', 'poly', 'rbf', 'sigmoid']
plt.bar(n, mses, align='center')
plt.xlabel('kernel')
plt.ylabel('Mean Squared Error')
plt.xticks(n, labels)
plt.title('Choice of Kernel - 2000 samples x 10 runs')

## Time differences in training model times# Time differences of training each model. 
start = time.time()
for i in range(10):
    df_train, df_train_labels, df_test, df_test_labels = split_data(df.sample(n=2000), 0.8, drop=drop2, scale=False)
    res = run_SVM_Regression(df_train, df_train_labels, df_test, df_test_labels)
end = time.time()
svm_time = end - start
print('SVM build time: ', svm_time)

start = time.time()
for i in range(10):
    df_train, df_train_labels, df_test, df_test_labels = split_data(df.sample(n=2000), 0.8, drop=drop2, scale=False)
    res = run_kNN_Regression(df_train, df_train_labels, df_test, df_test_labels)
end = time.time()
knn_time = end - start
print('KNN build time: ', knn_time)

## Radius nearest neighbors
# Test distance metrics
final_results = []

for metric in ['euclidean', 'manhattan', 'chebyshev', 'minkowski']:
    for i in range(100):
        results = []
        df_train, df_train_labels, df_test, df_test_labels = split_data(df.sample(n=2000), 0.8, drop=drop, scale=True)
        res = run_Radius_Regression(df_train, df_train_labels, df_test, df_test_labels, metric=metric)
        print('\n')
        results.append(res)
    final_results.append(results)

# Plot
avg = [[sum(i) / len(i) for i in zip(*x)] for x in final_results]
mses = [x[0] for x in avg]
n = [0, 1, 2, 3]
labels = ['euclidean', 'manhattan', 'chebyshev', 'minkowski']
plt.bar(n, mses, align='center')
plt.xlabel('metric')
plt.ylabel('Mean Squared Error')
plt.xticks(n, labels)
plt.title('Choice of Metric - 2000 samples x 100 runs')
axes = plt.gca()
axes.set_ylim([0.0, 0.05])