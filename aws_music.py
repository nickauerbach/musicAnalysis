import boto3
import pandas as pd
import numpy as np
import os
import soundfile as sf
import librosa
from scipy.fft import fft
from statistics import mean
from scipy.stats import entropy
import sklearn
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.utils.extmath import randomized_svd
import EntropyHub as eh
from sklearn.preprocessing import MinMaxScaler
import pickle

ACCESS_KEY = 'AKIA3MO27G46QCTSLV5C'
SECRET_KEY = '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'
REGION = 'us-east-1'
BUCKET_NAME = 'music-analysis-database'
library = pd.DataFrame(columns=["Song ID", "Sampling Rate", "Samples", "Raw Frequencies"])
matrixPCA = pd.DataFrame(columns = ["Track","STFT","specMatrix"])
pca_results = pd.DataFrame(columns=["25 Principal Components", "Explained Variance", "Explained Variance Ratios"])
MSE_results = pd.DataFrame(columns = ["MSE","Ci"])

# connect to S3 framework
s3_client = boto3.client(
    's3',
    aws_access_key_id = ACCESS_KEY,
    aws_secret_access_key = SECRET_KEY,
    region_name = REGION
)

s3_resource = boto3.resource(
    's3',
    aws_access_key_id = ACCESS_KEY,
    aws_secret_access_key = SECRET_KEY,
    region_name = REGION
)

# grab music, load audio, feed to library dataframe
def build_library():
    bucket = s3_resource.Bucket(bucket_name)
    global library
    for obj in bucket.objects.all():
        filename = obj.key.rsplit('/')[-1]
        client.download_file(bucket_name, obj.key, f'/tmp/track.flac')
        samps, sr = librosa.load(key[ "Key" ], sr = 44100, mono = True, offset = 0.0, duration = None)
        freqs = np.fft.fft(samps)
        library.loc[len(library.index)] = [keyString, sr, samps, freqs]

# run short time fourier transform, spectrogram extraction to run PCA
def PCA_prep():
    global matrixPCA
    matrixPCA["Track"] = library.iloc[:,0]
    matrixPCA["STFT"] = [librosa.stft(x) for x in library["Samples"]]
    matrixPCA["specMatrix"] = [librosa.amplitude_to_db(abs(x)) for x in matrixPCA["STFT"]]
    return matrixPCA

# run principal component analysis
def musicPCA(matrix):
    global pca_results
    standard = StandardScaler().fit_transform(matrix)
    pca = PCA(n_components = 25, svd_solver ='randomized')
    pca.fit_transform(standard)
    pca_results.loc[len(results.index)] = [pca.components_, pca.explained_variance_, pca.explained_variance_ratio_]
    return pca_results

# build metrics
def build_metrics():
    global library
    library["Processed Frequencies"] = np.abs(library["Raw Frequencies"])
    library["Average Amplitude"] = [np.mean(x, dtype = np.float64) for x in library["Samples"]]
    library["Average Frequency"] = [np.mean(x, dtype = np.float64) for x in library["Processed Frequencies"]]
    library["Shannon Entropy"] = [entropy(pd.Series(x).value_counts(normalize = True)) for x in library["Processed Frequencies"]]
    library["Zero Crossings"] = [librosa.zero_crossings(x, pad=False) for x in library["Samples"]]
    library["Spectral Centroids"] = [librosa.feature.spectral_centroid(x, 44100) for x in library["Samples"]]
    library["25 Principal Components"] = pca_results["25 Principal Components"]
    library["Explained Variance"] = pca_results["Explained Variance"]
    library["Explained Variance Ratios"] = pca_results["Explained Variance Ratios"]
    library["PCs TEV"] = [np.sum(x) for x in library["Explained Variance Ratios"]]

# build entropyhub multiscale entropy + integral complexity index based on audio spectral centroids
def EntropyHub_MSE():
    Mobj = eh.MSobject('SampEn', m = 4, r = 1.25)
    global library
    global MSE_results
    spec_cents = library["Spectral Centroids"]
    for list in scs:
        list = np.array(list)
        MSE, Ci = eh.rMSEn(list, Mobj, Scales = 5, F_Order = 3, F_Num = 0.6)
        results.loc[len(results.index)] = MSE, Ci
    library["MSE"] = MSE_results["MSE"]
    library["Ci"] = MSE_results["Ci"]

# normalize data 0-1
def normalizer(col):
    scaler = MinMaxScaler()
    values = library[col]
    scaledValues = scaler.fit_transform(values)
    return scaledValues

# send library of metrics to S3
def df_to_s3_pckl(df):
    buffer = io.BytesIO()
    df.to_pickle(buffer)
    buffer.seek(0)
    obj = resource.Object(bucket_name, f'/data.pkl')
    obj.put(Body=buffer.getvalue())

# function calls
build_library()
PCA_prep()
[musicPCA(x) for x in matrixPCA["specMatrix"]]
build_metrics()
build_MSE()
library["Shannon Entropy"] = normalizer("Shannon Entropy")
library["Complexity Index"] = normalizer("Ci")
library["PCA TEV"] = normalizer("PCA TEV")
df_to_s3_pckl(library)

# pickle all dataframes
# with open("library", "wb") as f:
#     pickle.dump(library, f)
#
# with open("pca", "wb") as f:
#     pickle.dump(pca_results, f)
#
# with open("mse", "wb") as f:
#     pickle.dump(mse_results, f)





