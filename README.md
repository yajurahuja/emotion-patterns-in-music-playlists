# Emotion Patterns in Music Playlists

Music streaming services such as Spotify are revolutionizing the music world, enabling a
transition from artist-created bundles of songs (CDs) to user-created playlists. Different
logics may be applied in the generation of a playlist: they can contain songs of a similar
genre (e.g. “Rock playlist”), fit to a particular occasion (e.g. “New year’s eve party”), to a
particular context (e.g. “Gym”), to a particular mood (e.g. “Happy”) and so on.

The goal of the project is to unravel the emotion patterns underlying the sequences of songs
in a playlist using automatic approaches of Emotion Detection on the lyrics. Emotion
Detection is a novel and promising field of study of Natural Language Understanding, which
is able to automatically infer what are the emotions expressed in a text.

In the context of this project we had to:
1. Select an appropriate playlist dataset among the ones available on the web
2. Collect the lyrics associated to each song through an automatic approach
3. Study the state-of-the-art in Emotion Detection
4. Extract the emotions present in each song using an Emotion Detection tool
5. Analyze the experimental results statistically to unravel emotion patterns in the playlists


Before running any script, please install dependencies

    pip install -r requirements.txt

## Emotion Classification

In order to provide emotion classification of songs lyrics we provided with this
repository already trained models. We trained three different model, each one releated 
to a different version of the dataset. Specifically we trained our model on the
following input combinations:
 - MoodyLyrics alone
 - MoodyLyrics4Q alone
 - MoodyLyrics + MoodyLyrics4Q

 For more details about those models, please refer to what is written in the
 report for this repo contained in the `Report` folder.

 Using the code in this repository, lyrics can be classified at three levels:
  1. **Lyric level**: using the function `classify(sid, artist, title)` of the `src/emoclassify.py` script
  2. **Playlist level**: using the function `robust_classify(playlist_vect)` from the `src/playlist_classify.py` script  
  3. **Spotify's dataset slice level**: using the functino `classify_slice(slice_path)` from the `src/slice_classify.py` script

For more information about those functions please refer to their respective scripts and
to the report.

## Utility Scripts

### lyrics_downloader.py

This script simply downloads the lyric of the songs contained
in any CSV file formatted in a similar way to MoodyLyrics dataset
files (`Index`,`Artist`,`Song`,`Emotion`). For a better understanding
of the options wich can be used with this script, please run:

`python3 lyrics_downloader.py -h`

From the `src` folder. If you want to test it with the dataset provided in
this repository, please run:

`python3 lyrics_downloader.py -i datasets/moodylyrics_raw.csv -o LYRICS_DIR -s`

The script will download the lyrics for the songs listed into the `src/datasets/moodylyrics.csv`
into the `src/LYRICS_DIR` folder. Each file will follow this name convention:
`EMOTION_ARTIST_SONG-TITLE`.


### LyricsManager.py

Map Spotify track URIs to LyricsWiki, and download the lyrics in a folder.

- Download and unzip [MoodyLyrics](http://softeng.polito.it/erion/MoodyLyrics.zip)
    - Convert `ml_raw.xlsx` to `ml_raw.csv` (to be better documented)
- Download and unzip the MPD
- run it


        python src/dataset_parsers/LyricsManager.py -ml /Users/pasquale/Desktop/MoodyLyrics/ml_raw.csv -i /Users/pasquale/Desktop/mpd.v1/data/ -o ./tmp/


### Demo

In order to run the demo web application you need to install the dependencies:

        pip install -r requirements.txt
        python -m spacy download en_core_web_lg


After that, the web app server can be executed by running:


        FLASK_APP=index.py flask run

