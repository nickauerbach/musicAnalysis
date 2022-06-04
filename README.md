# Music Analysis

Data pipeline to feature engineer entropy/complexity metrics of audio data. Comparative visualization notebook and excel spreadsheet included. 

Initial dataset can be found [here](https://open.spotify.com/playlist/0hBQxz37zeQKCyDDPAGvEa?si=734b588a1183455e).

Lossless audio pulled from [TunElf Spotify Converter](https://www.tunelf.com/spotibeat-audio-converter.html).

Run aws_music.py on AWS Linux EC2 r5 Instance/S3 bucket.

See selectedSongs and visualizations for visualized data set.

TODO: Implement PyTorch Audio Feature Extraction (comparable to librosa?) / RNN on sample time series?
