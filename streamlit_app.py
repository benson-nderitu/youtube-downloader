import base64
import os
from pathlib import Path

import streamlit as st
from pytubefix import YouTube
from pytubefix.exceptions import RegexMatchError

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
        audio_streams, video_streams = get_streams(url)
        col0, col1, col2 = st.columns(
            [0.75, 0.65, 2], gap="medium", vertical_alignment="bottom"
        )
        with col0:
            if download_type == "audio(mp3)":
                stream_options = {f"{s.abr} - {s.mime_type}": s for s in audio_streams}
                audio_quality = st.selectbox(
                    "audio quality", options=list(stream_options.keys())
                )
            else:
                stream_options = {
                    f"{s.resolution} - {s.mime_type}": s for s in video_streams
                }
                video_quality = st.selectbox(
                    "video quality", options=list(stream_options.keys())
                )

        if url:
            stream = (
                stream_options[audio_quality]
                if download_type == "audio(mp3)"
                else stream_options[video_quality]
            )
            itag = stream.itag
            # st.write(f"Selected Stream itag: {itag}")
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
                    video_download(url, itag)
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
        audio_streams, video_streams = get_streams(first_url)
        message = st.empty()
        col0, col1, col2 = st.columns(
            [0.5, 0.65, 2], gap="medium", vertical_alignment="bottom"
        )
        with col0:
            if download_type == "audio(mp3)":
                stream_options = {f"{s.abr} - {s.mime_type}": s for s in audio_streams}
                audio_quality = st.selectbox(
                    "audio quality", options=list(stream_options.keys()), disabled=True
                )

            else:
                stream_options = {
                    f"{s.resolution} - {s.mime_type}": s for s in video_streams
                }
                video_quality = st.selectbox(
                    "video quality", options=list(stream_options.keys()), disabled=True
                )

        for url in url_list:
            if url:
                stream = (
                    stream_options[audio_quality]
                    if download_type == "audio(mp3)"
                    else stream_options[video_quality]
                )
                itag = stream.itag
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
                if not url:
                    message.warning("Please enter a valid URL.", icon="⚠️")
                    st.stop()

                if download_type == "audio(mp3)":
                    download_multiple_audio(url)
                else:
                    download_multiple_video(url, itag)
            len_urls = len(url_list)
            st.success(
                body=f"All {len_urls} files have been downloaded!",
                icon=":material/done_all:",
            )
        if col2.button(
            label="Clear",
            on_click=clear_multiple_url,
            icon=":material/mop:",
            type="tertiary",
            key="clear_multiple_url",
        ):
            st.rerun()

blank_lines(1)

if st.toggle("Show video(s) info", False, help="Show video(s) info"):
    with st.spinner("Loading..."):
        if download_mode == "one":
            if url:
                container = st.container(border=True)
                col1, col2 = container.columns([1, 1])
                with col1:
                    yt = YouTube(url)
                    st.markdown(f"**Title:** {yt.title}")
                    st.markdown(f"**Length:** {yt.length} sec")

                with col2:
                    thumbnail = yt.thumbnail_url
                    st.image(thumbnail)
        if download_mode == "multiple":
            if urls:
                for index, url in enumerate(
                    url_list
                ):  # Enumerate to get both index and value
                    if index % 3 == 0:
                        col1, col2, col3 = st.columns(
                            3, border=True
                        )  # Create three columns
                        with col1:
                            yt = YouTube(url.strip())
                            st.markdown(f"**Title:** {yt.title}")
                            st.markdown(f"**Length:** {yt.length} sec")

                    elif index % 3 == 1:
                        with col2:
                            yt = YouTube(url.strip())
                            st.markdown(f"**Title:** {yt.title}")
                            st.markdown(f"**Length:** {yt.length} sec")

                    else:
                        with col3:
                            yt = YouTube(url.strip())
                            st.markdown(f"**Title:** {yt.title}")
                            st.markdown(f"**Length:** {yt.length} sec")
