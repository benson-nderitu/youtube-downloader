import os
from pathlib import Path

import streamlit as st
import wx
from pytube import YouTube
from pytubefix import YouTube
from pytubefix.exceptions import RegexMatchError

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


# Function to get the default downloads folder based on the OS
def get_default_download_folder():
    if os.name == "nt":  # Windows
        return str(Path.home() / "Downloads")
    elif os.name == "posix":  # macOS and Linux
        return str(Path.home() / "Downloads")
    return str(Path.home())  # Fallback to home directory


# Set default folder
default_folder = get_default_download_folder()
folder_path = default_folder  # Initialize folder_path with default value

with col4:
    # st.write(f"Default folder: {folder_path}")
    app = wx.App(False)  # Create a new app instance
    if st.button(
        "Select a folder to save",
        icon=":material/folder_open:",
        type="secondary",
        use_container_width=True,
    ):
        dialog = wx.DirDialog(
            None, "Select a folder:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON
        )

        if dialog.ShowModal() == wx.ID_OK:
            folder_path = dialog.GetPath()  # Update folder_path with user-selected path
            st.success(f"Selected folder: {folder_path}", icon="✅")
        else:
            st.warning(f"Using default folder: {folder_path}")

        dialog.Destroy()
# st.write(f"Selected folder: {folder_path}")
# folder_path = None  # Reset folder_path to None


# ---------------------------------------------------
#             Functions
# ---------------------------------------------------
def audio_download(url: str, destination: str) -> None:
    try:
        if not url.strip():
            st.warning("Please enter a valid YouTube URL")
            return
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()

        if not video:
            st.error("No audio stream found for this video")
            return
        out_file = video.download(output_path=destination, skip_existing=True)
        base, ext = os.path.splitext(out_file)
        new_file = base + ".mp3"
        # Check if MP3 file already exists
        if os.path.exists(new_file):
            os.remove(out_file)  # Clean up the temporary file
            st.info(
                f"😩 File already exists: {os.path.basename(new_file)}",
                icon=":material/error:",
            )
            return
        os.rename(out_file, new_file)
        st.success(f"{yt.title} has been successfully downloaded.", icon="✅")

    except RegexMatchError:
        st.error("Please enter a valid YouTube URL")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


def video_download(url: str, destination: str, itag: int) -> None:
    """
    Downloads video from YouTube URL and converts it to MP4.

    Args:
        url (str): YouTube video URL
        destination (str): Output directory path

    Raises:
        RegexMatchError: If URL is invalid
        Exception: For other errors during download/conversion
    """
    try:
        if not url.strip():
            st.warning("Please enter a valid YouTube URL")
            return

        # Create YouTube object and download video
        yt = YouTube(url)
        # yt.streams.filter(file_extension='mp4')
        video = yt.streams.get_highest_resolution()
        # video = yt.streams.get_by_itag(itag)
        # video = yt.streams.get_highest_resolution() or yt.streams.get_by_itag(itag)

        if not video:
            st.error("No Video stream found for this video")
            return

        # Download and convert to MP4
        out_file = video.download(output_path=destination, skip_existing=True)
        base, ext = os.path.splitext(out_file)
        new_file = base + ".mp4"
        os.rename(out_file, new_file)
        st.success(f"{yt.title} has been successfully downloaded.", icon="✅")

    except RegexMatchError:
        st.error("Please enter a valid YouTube URL")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


def get_streams(url=None):
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        st.warning("Please enter a valid YouTube URL.", icon=":material/info:")
        return [], []  # Return empty lists if the URL is invalid
    yt = YouTube(url)
    audio_streams = yt.streams.filter(only_audio=True)
    video_streams = yt.streams.filter(adaptive=True, only_video=True)
    return audio_streams, video_streams


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

                if folder_path is None:
                    message.warning(
                        "Please select a folder to save the file.", icon="⚠️"
                    )
                    st.stop()

                if download_type == "audio(mp3)":
                    audio_download(url, folder_path)
                else:
                    video_download(url, folder_path, itag)
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

                if folder_path is None:
                    message.warning(
                        "Please select a folder to save the file.", icon="⚠️"
                    )
                    st.stop()

                if download_type == "audio(mp3)":
                    for index, url in enumerate(url_list):
                        audio_download(url, folder_path)
                else:
                    for index, url in enumerate(url_list):
                        video_download(url, folder_path, itag)
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
