# -*- coding: utf-8 -*-
"""
Created on Sat Nov  9 12:54:08 2024

@author: angel
"""

#pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pytube
#pip install moviepy
#pip install yt-dlp

import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import yt_dlp as youtube_dl
#from pytube import YouTube
#from moviepy.editor import AudioFileClip

# Configuration de l'API Google
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def get_authenticated_service():
    # Authentification avec le fichier credentials.json
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "credentials.json", scopes)
    credentials = flow.run_local_server(port=0)  # Utilise un serveur local pour l'authentification
    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def get_playlist_videos(youtube, playlist_id):
    # Récupérer les vidéos de la playlist
    video_urls = []
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=5000
    )
    while request:
        response = request.execute()
        for item in response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_urls.append(f"https://www.youtube.com/watch?v={video_id}")
        request = youtube.playlistItems().list_next(request, response)
    return video_urls

def download_video_as_wav(url, output_path="downloads"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'ffmpeg_location': r'C:\ffmpeg-2025-05-29-git-75960ac270-full_build\bin',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        #print(f"Téléchargé et converti : {info_dict['title']}.wav")

"""
def download_video_as_wav(url, output_path="downloads"):
    # Télécharger la vidéo et la convertir en WAV
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()
    mp4_path = stream.download(output_path)
    
    wav_path = os.path.splitext(mp4_path)[0] + '.wav'
    with AudioFileClip(mp4_path) as audio:
        audio.write_audiofile(wav_path, codec='pcm_s16le')  # Codec pour format WAV
    
    os.remove(mp4_path)  # Supprimer le fichier MP4 après conversion
    print(f"Téléchargé et converti : {wav_path}")
"""

def main():

    dir_path = "downloads"
    #dir_path = "tryhard"

    # Créer le dossier de téléchargement
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print("Dossier "+dir_path+" créé.")
    
    # Vérifie que credentials.json existe
    if not os.path.exists("credentials.json"):
        print("Erreur : Le fichier 'credentials.json' est introuvable.")
        return

    try:
        # Se connecter à l'API YouTube
        print("Connexion à l'API YouTube...")
        youtube = get_authenticated_service()
        print("Connexion réussie.")
        
        # ID de la playlist 
        #download
        playlist_id = "PLw3P29g6s_PeYszc-uwrjFf3-lGS0U-wb"
        # tryhard
        #playlist_id = "PLO2J-X1ZFuLlnnR-sJUyhjnW_imk8sPFi"

        # Récupérer les URLs des vidéos dans la playlist
        print(f"Récupération des URLs de la playlist {playlist_id}...")
        video_urls = get_playlist_videos(youtube, playlist_id)
        print(f"Récupération terminée : {len(video_urls)} vidéos trouvées.")
        
        # Télécharger chaque vidéo et convertir en WAV
        for index, url in enumerate(video_urls, start=1):
            try:
                # si le fichier existe déjà, on ne le télécharge pas
                file_name = os.path.join(dir_path, f"{index}.webm")
                if os.path.exists(file_name):
                    print(f"Le fichier {file_name} existe déjà, passage au suivant.")
                    continue
                print(f"Téléchargement et conversion de la vidéo {index}/{len(video_urls)} : {url}")
                download_video_as_wav(url, output_path=dir_path)
                print(f"Vidéo {index} téléchargée et convertie avec succès.")
            except Exception as e:
                print(f"Erreur lors du téléchargement de la vidéo {index} : {e}")
        
        print("Traitement de la playlist terminé.")

    except Exception as e:
        print(f"Erreur critique lors de l'exécution : {e}")

if __name__ == "__main__":
    main()
