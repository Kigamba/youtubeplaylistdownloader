import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION", "r") as fh:
    version = fh.read()

setuptools.setup(
    name="youtube-playlist-downloader",
    version=version,
    author="Krunal Soni",
    author_email="krunalnsoni@gmail.com",
    description="Python library to download youtube playlist for a user.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/planetsoni/youtubeplaylistdownloader",
    packages=setuptools.find_packages(exclude=["test"]),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    license="Apache 2.0",
    # Dependent packages (distributions)
    install_requires=["google_auth_oauthlib", "google-api-python-client"],
    python_requires='>=3.6',
    entry_points={
        'console_scripts':
        ['youtube-playlist-downloader=youtube_playlist_downloader.main:main'],
    },
)
