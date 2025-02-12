import base64
import os
from pathlib import Path

import streamlit as st
from pytubefix import YouTube
from pytubefix.exceptions import RegexMatchError


# ---------------------------------------------------
#             Functions
# ---------------------------------------------------
def audio_download(url: str) -> None:
    try:
        if not url.strip():
            st.warning("Please enter a valid YouTube URL")
            return
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()

        if not video:
            st.error("No audio stream found for this video")
            return

        # Download to temporary location
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        out_file = video.download(output_path=temp_dir)
        base, ext = os.path.splitext(out_file)
        new_file = base + ".mp3"
        os.rename(out_file, new_file)

        # Create and display download link
        with open(new_file, "rb") as f:
            bytes_data = f.read()
        b64 = base64.b64encode(bytes_data).decode()
        download_filename = os.path.basename(new_file)
        st.markdown(
            f'<a href="data:audio/mp3;base64,{b64}" download="{download_filename}">📥 Download {download_filename}</a>',
            unsafe_allow_html=True,
        )
        st.success(f"{yt.title} is ready for download.", icon="✅")

        # Clean up after creating download link
        os.remove(new_file)

    except RegexMatchError:
        st.error("Please enter a valid YouTube URL")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


def video_download(url: str, itag: int) -> None:
    try:
        if not url.strip():
            st.warning("Please enter a valid YouTube URL")
            return

        yt = YouTube(url)
        video = yt.streams.get_highest_resolution()

        if not video:
            st.error("No Video stream found for this video")
            return

        # Download to temporary location
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        out_file = video.download(output_path=temp_dir)
        base, ext = os.path.splitext(out_file)
        new_file = base + ".mp4"
        os.rename(out_file, new_file)

        # Create and display download link
        with open(new_file, "rb") as f:
            bytes_data = f.read()
        b64 = base64.b64encode(bytes_data).decode()
        download_filename = os.path.basename(new_file)
        st.markdown(
            f'<a href="data:video/mp4;base64,{b64}" download="{download_filename}">📥 Download {download_filename}</a>',
            unsafe_allow_html=True,
        )
        st.success(f"{yt.title} is ready for download.", icon="✅")

        # Clean up after creating download link
        os.remove(new_file)

    except RegexMatchError:
        st.error("Please enter a valid YouTube URL")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


def download_multiple_audio(url_list: list) -> None:
    try:
        # Create progress bar
        progress_bar = st.progress(0)
        total_urls = len(url_list)

        for index, url in enumerate(url_list, 1):
            if not url.strip():
                continue

            try:
                yt = YouTube(url.strip())
                video = yt.streams.filter(only_audio=True).first()

                if not video:
                    st.error(f"No audio stream found for: {yt.title}")
                    continue

                # Download to temporary location
                temp_dir = "temp"
                os.makedirs(temp_dir, exist_ok=True)
                out_file = video.download(output_path=temp_dir)
                base, ext = os.path.splitext(out_file)
                new_file = base + ".mp3"
                os.rename(out_file, new_file)

                # Create and display download link
                with open(new_file, "rb") as f:
                    bytes_data = f.read()
                b64 = base64.b64encode(bytes_data).decode()
                download_filename = os.path.basename(new_file)
                st.markdown(
                    f'<a href="data:audio/mp3;base64,{b64}" download="{download_filename}">📥 Download {download_filename}</a>',
                    unsafe_allow_html=True,
                )
                st.success(f"{yt.title} is ready for download.", icon="✅")

                # Update progress
                progress = int(index / total_urls * 100)
                progress_bar.progress(progress)

                # Clean up after creating download link
                os.remove(new_file)

            except Exception as e:
                st.error(f"Error processing URL {url}: {str(e)}")
                continue

        progress_bar.empty()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


def download_multiple_video(url_list: list, itag: int) -> None:
    try:
        # Create progress bar
        progress_bar = st.progress(0)
        total_urls = len(url_list)

        for index, url in enumerate(url_list, 1):
            if not url.strip():
                continue

            try:
                yt = YouTube(url.strip())
                video = yt.streams.get_highest_resolution()

                if not video:
                    st.error(f"No video stream found for: {yt.title}")
                    continue

                # Download to temporary location
                temp_dir = "temp"
                os.makedirs(temp_dir, exist_ok=True)
                out_file = video.download(output_path=temp_dir)
                base, ext = os.path.splitext(out_file)
                new_file = base + ".mp4"
                os.rename(out_file, new_file)

                # Create and display download link
                with open(new_file, "rb") as f:
                    bytes_data = f.read()
                b64 = base64.b64encode(bytes_data).decode()
                download_filename = os.path.basename(new_file)
                st.markdown(
                    f'<a href="data:video/mp4;base64,{b64}" download="{download_filename}">📥 Download {download_filename}</a>',
                    unsafe_allow_html=True,
                )
                st.success(f"{yt.title} is ready for download.", icon="✅")

                # Update progress
                progress = int(index / total_urls * 100)
                progress_bar.progress(progress)

                # Clean up after creating download link
                os.remove(new_file)

            except Exception as e:
                st.error(f"Error processing URL {url}: {str(e)}")
                continue

        progress_bar.empty()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
