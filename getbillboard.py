# ライブラリの読み込み
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import datetime
import configparser
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe

# 別ファイルで用意したID/パスワード設定ファイルを読み込む準備
config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')
# セクションを指定して読み込む
config = config_ini['DEFAULT']
client_id = config.get('client_id')
client_secret = config.get('client_secret')

# GoogleSeet

# GoogleSheetのお決まりの文句
# 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']

#ダウンロードしたjsonファイル名をクレデンシャル変数に設定 パスはconfig.ini内で指定

credentials = Credentials.from_service_account_file(config.get("json_key"), scopes=scope)

#OAuth2の資格情報を使用してGoogle APIにログイン
gc = gspread.authorize(credentials)

#スプレッドシートIDを変数に格納する
SPREADSHEET_KEY = '1zEl_8cH0DzvQ5W5FqC_jxFVqfixDVJ9Y9K6AmP2oR6Q'


# Spotipy

# Spotipy認証の準備
client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(client_id, client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager,language='ja')

# BillboardJapan100のプレイリストからTrackの情報を取得する
playlist_tracks = spotify.playlist_tracks('54WBnoUJ9oAFo5OCes3SVg',market='JP',limit=5,fields='items.track.popularity,items.track.external_ids,items.track.id,items.track.type,items.track.name,items.track.artists,items.track.album.release_date')

# 取得した情報から必要な項目を抜き出してdataframeに格納する
rank = 1
today = datetime.date.today()
cols = ['date','rank','track_name','popularity','spotify_id','isrc','artist_name','artist_id']
df = pd.DataFrame(index=[], columns=cols)

for item in playlist_tracks['items']:
    track = item['track']
    album = track['album']
    artist = track['artists']
    ex_id = track['external_ids']
    spotify_id = track['id']
    release_date = album['release_date']
    popularity = track['popularity']
    track_name = track['name']
    artist_list = artist[0]
    artist_name = artist_list['name']
    artist_id = artist_list['id']
    isrc = ex_id['isrc']
    print(today,rank,track_name,popularity,release_date,isrc,spotify_id,artist_name,artist_id)
    df2 = pd.DataFrame([[str(today),rank,track_name,popularity,spotify_id,isrc,artist_name,artist_id]],columns=['date','rank','track_name','popularity','spotify_id','isrc','artist_name','artist_id'])
    df = pd.concat([df,df2])
    rank = (rank+1)

# dataframeからGoogleSheetに値を格納

# GoogleSheetのブックを開きシートを選択
workbook = gc.open_by_key(SPREADSHEET_KEY)
worksheets = workbook.worksheets()
worksheet = workbook.worksheet('シート1')

# シートの最下段の行数を取得
a_col_array = worksheet.col_values(1)
last_row_idx = len(a_col_array)
new_low = int(last_row_idx) + 1

# 最下段の下にdataframeを値を格納
set_with_dataframe(workbook.worksheet('シート1'),df,include_column_header=False,row=new_low)

