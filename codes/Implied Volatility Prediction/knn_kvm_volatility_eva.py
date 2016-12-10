import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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

# Main
df = pd.read_csv('Quiz5_results.csv')

# Filter out rows without labels
mask = df['IMP_VOLATILITY'] != 0.0
df = df[mask]

# Filter out predicted labels that are more than 1% away (Assumption: those labels may be American options)
mask1 = (df['IMP_VOLATILITY'] - df['IV_CLASSIC']).abs() <= 0.01
mask2 = (df['IMP_VOLATILITY'] - df['IV_MULLER']).abs() <= 0.01
mask3 = (df['IMP_VOLATILITY'] - df['IV_NEWTON']).abs() <= 0.01
mask4 = (df['IMP_VOLATILITY'] - df['IV_HALLEY']).abs() <= 0.01

# Calculate Error Stats for each method
results = []
results.append(compute_measure(df[mask1]['IV_CLASSIC'], df[mask1]['IMP_VOLATILITY']))
results.append(compute_measure(df[mask2]['IV_MULLER'], df[mask2]['IMP_VOLATILITY']))
results.append(compute_measure(df[mask3]['IV_NEWTON'], df[mask3]['IMP_VOLATILITY']))
results.append(compute_measure(df[mask4]['IV_HALLEY'], df[mask4]['IMP_VOLATILITY']))

# Plot
mses = [x[0] for x in results]
n = [0, 1, 2, 3]
labels = ['BISECTION', 'MULLER', 'NEWTON', 'HALLEY']
plt.bar(n, mses, align='center')
plt.xlabel('Method')
plt.ylabel('Mean Squared Error')
plt.xticks(n, labels)
plt.title('Root Finding Method')

# Results table as dataframe
results_df = pd.DataFrame(results, columns=['MSE', 'MEAN', 'MEDIAN', 'MAX', 'MIN'], index=['BISECTION', 'MULLER', 'NEWTON', 'HALLEY'])