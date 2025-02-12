import base64
import os
import time
from pathlib import Path
from urllib.error import HTTPError

import streamlit as st
from pytubefix import YouTube
from pytubefix.exceptions import RegexMatchError, VideoUnavailable

from utils import (
    audio_download,
    download_multiple_audio,
    download_multiple_video,
    video_download,
)

st.set_page_config(
    page_title="Youtube Downloader",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------
#     CUSTOM CSS TO REMOVE PADDING
# ------------------------------------------------------------
st.markdown(
    """
        <style>
            .st-emotion-cache-1jicfl2,
            .stMainBlockContainer.block-container {
                width: 100%;
                padding: 0rem 5rem 5rem;
                min-width: auto;
                max-width: initial;
                }
            @media (max-width: 768px) {
                .st-emotion-cache-1jicfl2,
                .stMainBlockContainer.block-container {
                    padding: 0rem 2rem 3rem;
                }
            }
        </style>
            """,
    unsafe_allow_html=True,
)


def blank_lines(x):
    for _ in range(x):
        st.write("\n")


blank_lines(2)
# ---------------------------------------------------
#             Sidebar
# ---------------------------------------------------
st.subheader(":primary[:material/youtube_activity: Youtube Downloader]")

col1, col2, col4 = st.columns(3, vertical_alignment="bottom")
download_mode = col1.selectbox("Mode", ["one", "multiple"])
download_type = col2.selectbox("Type", ["audio(mp3)", "video(mp4)"])


@st.cache_data
def create_download_link(file_path, file_name):
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    b64 = base64.b64encode(bytes_data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">Download {file_name}</a>'


# ---------------------------------------------------
#             Main content
# ---------------------------------------------------
def clear_single_url():
    st.session_state["singleURL"] = ""


def clear_multiple_url():
    st.session_state["multipleURLs"] = ""


blank_lines(1)
with st.container(border=True):
    if download_mode == "one":
        url = st.text_input("Enter YouTube URL", key="singleURL")
        message = st.empty()  # Placeholder for warnings/messages
        col1, col2 = st.columns([1, 3], gap="medium", vertical_alignment="bottom")

        if col1.button(
            "Download",
            type="primary",
            icon=":material/download:",
            use_container_width=True,
        ):
            with st.spinner("Downloading..."):
                if not url:
                    message.warning("Please enter a valid URL.", icon="⚠️")
                    st.stop()
                if download_type == "audio(mp3)":
                    audio_download(url)
                else:
                    video_download(url)
        if col2.button(
            label="Clear",
            on_click=clear_single_url,
            icon=":material/mop:",
            type="tertiary",
            key="clear_single_url",
        ):
            st.rerun()
    else:
        urls = st.text_area(
            "YouTube URLs (separate by commas)", height=100, key="multipleURLs"
        )
        url_list = urls.split(",")  # Split the input string into a list of URLs
        first_url = url_list[0].strip() if url_list else None
        message = st.empty()
        col1, col2 = st.columns([1, 3], gap="medium", vertical_alignment="bottom")
        if (
            col1.button(
                "Download All",
                icon=":material/download:",
                type="primary",
                use_container_width=True,
            )
            and urls
        ):
            with st.spinner("Downloading..."):
                if not urls:
                    message.warning("Please enter a valid URL.", icon="⚠️")
                    st.stop()

                if download_type == "audio(mp3)":
                    download_multiple_audio(url_list)
                else:
                    download_multiple_video(url_list)
            len_urls = len(url_list)

        if col2.button(
            label="Clear",
            on_click=clear_multiple_url,
            icon=":material/mop:",
            type="tertiary",
            key="clear_multiple_url",
        ):
            st.rerun()

blank_lines(1)


def get_youtube_object(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            yt = YouTube(url.strip())
            return yt
        except HTTPError as e:
            if e.code == 403:
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait 2 seconds before retrying
                    continue
                st.error(f"Access forbidden (HTTP 403). Please try again later.")
            else:
                st.error(f"HTTP Error: {str(e)}")
        except VideoUnavailable:
            st.error(f"Video is unavailable")
        except RegexMatchError:
            st.error(f"Invalid YouTube URL")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        return None


if st.toggle("Show video(s) info", False, help="Show video(s) info"):
    with st.spinner("Loading..."):
        if download_mode == "one":
            if url:
                container = st.container(border=True)
                col1, col2 = container.columns([1, 1])
                with col1:
                    yt = get_youtube_object(url)
                    if yt:
                        st.markdown(f"**Title:** {yt.title}")
                        st.markdown(f"**Length:** {yt.length} sec")
                        with col2:
                            thumbnail = yt.thumbnail_url
                            st.image(thumbnail)

        if download_mode == "multiple":
            if urls:
                for index, url in enumerate(url_list):
                    if index % 3 == 0:
                        col1, col2, col3 = st.columns(3, border=True)
                        with col1:
                            yt = get_youtube_object(url)
                            if yt:
                                st.markdown(f"**Title:** {yt.title}")
                                st.markdown(f"**Length:** {yt.length} sec")
                    elif index % 3 == 1:
                        with col2:
                            yt = get_youtube_object(url)
                            if yt:
                                st.markdown(f"**Title:** {yt.title}")
                                st.markdown(f"**Length:** {yt.length} sec")
                    else:
                        with col3:
                            yt = get_youtube_object(url)
                            if yt:
                                st.markdown(f"**Title:** {yt.title}")
                                st.markdown(f"**Length:** {yt.length} sec")
