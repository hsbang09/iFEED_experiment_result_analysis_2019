
import numpy as np
from scipy.stats import pearsonr, spearmanr
from scipy import stats
import pandas as pd
import math

def CronbachAlpha(itemscores):
    itemscores = np.asarray(itemscores)
    itemvars = itemscores.var(axis=1, ddof=1)
    tscores = itemscores.sum(axis=0)
    nitems = len(itemscores)
    return nitems / (nitems-1.) * (1 - itemvars.sum() / tscores.var(ddof=1))

def calculate_pearsonr(df, decimal=2):
    df = df.dropna()._get_numeric_data()
    dfcols = pd.DataFrame(columns=df.columns)
    rmat = dfcols.transpose().join(dfcols, how='outer')
    pmat = dfcols.transpose().join(dfcols, how='outer')
    ciLow = dfcols.transpose().join(dfcols, how='outer')
    ciHigh = dfcols.transpose().join(dfcols, how='outer')
    for r in df.columns:
        for c in df.columns:
            rho, p = pearsonr(df[r], df[c])
            rmat[r][c] = round(rho, decimal)
            pmat[r][c] = round(p, decimal)
            if r == c:
                ciLow[r][c] = 0
                ciHigh[r][c] = 0
            else:
                lo, hi = getCorrelationConfidenceInterval(rho, len(df[r].values))
                ciLow[r][c] = round(lo, decimal)
                ciHigh[r][c] = round(hi, decimal)
    return rmat, pmat, ciLow, ciHigh

def calculate_spearmanr(df, decimal=2):
    df = df.dropna()._get_numeric_data()
    dfcols = pd.DataFrame(columns=df.columns)
    rmat = dfcols.transpose().join(dfcols, how='outer')
    pmat = dfcols.transpose().join(dfcols, how='outer')
    ciLow = dfcols.transpose().join(dfcols, how='outer')
    ciHigh = dfcols.transpose().join(dfcols, how='outer')
    for r in df.columns:
        for c in df.columns:
            rho, p = spearmanr(df[r], df[c])
            rmat[r][c] = round(rho, decimal)
            pmat[r][c] = round(p, decimal)
            if r == c:
                ciLow[r][c] = 0
                ciHigh[r][c] = 0
            else:
                _,_,lo,hi = spearmanr_ci(df[r], df[c])
                # lo, hi = getCorrelationConfidenceInterval(rho, len(df[r].values))
                ciLow[r][c] = round(lo, decimal)
                ciHigh[r][c] = round(hi, decimal)
    return rmat, pmat, ciLow, ciHigh

def getCorrelationConfidenceInterval(r, N, alpha=0.95):
    #https://stats.stackexchange.com/questions/18887/how-to-calculate-a-confidence-interval-for-spearmans-rank-correlation

    stderr = 1 / math.sqrt(N - 3)
    z = stats.norm.ppf(1 - alpha / 2)
    lo = math.tanh(math.atanh(r) - z * stderr)
    hi = math.tanh(math.atanh(r) + z * stderr)
    return lo, hi

def spearmanr_ci(x,y,alpha=0.05):
    ''' calculate Pearson correlation along with the confidence interval using scipy and numpy
    source: https://zhiyzuo.github.io/Pearson-Correlation-CI-in-Python/

    Parameters
    ----------
    x, y : iterable object such as a list or np.array
      Input for correlation calculation
    alpha : float
      Significance level. 0.05 by default

    Returns
    -------
    r : float
      Pearson's correlation coefficient
    pval : float
      The corresponding p value
    lo, hi : float
      The lower and upper bound of confidence intervals
    '''

    r, p = spearmanr(x,y)
    r_z = np.arctanh(r)
    se = 1/np.sqrt(x.size-3)
    z = stats.norm.ppf(1-alpha/2)
    lo_z, hi_z = r_z-z*se, r_z+z*se
    lo, hi = np.tanh((lo_z, hi_z))
    return r, p, lo, hi

def pearsonr_ci(x,y,alpha=0.05):
    ''' calculate Pearson correlation along with the confidence interval using scipy and numpy
    source: https://zhiyzuo.github.io/Pearson-Correlation-CI-in-Python/

    also refer to:
    https://en.wikipedia.org/wiki/Fisher_transformation

    Parameters
    ----------
    x, y : iterable object such as a list or np.array
      Input for correlation calculation
    alpha : float
      Significance level. 0.05 by default

    Returns
    -------
    r : float
      Pearson's correlation coefficient
    pval : float
      The corresponding p value
    lo, hi : float
      The lower and upper bound of confidence intervals
    '''

    r, p = pearsonr(x,y)
    r_z = np.arctanh(r)
    se = 1/np.sqrt(x.size-3)
    z = stats.norm.ppf(1-alpha/2)
    lo_z, hi_z = r_z-z*se, r_z+z*se
    lo, hi = np.tanh((lo_z, hi_z))
    return r, p, lo, hi