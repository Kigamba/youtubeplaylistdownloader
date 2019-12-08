import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="youtube-playlist-downloader",
    version="0.0.1",
    author="Krunal Soni",
    author_email="krunalnsoni@gmail.com",
    description="Python library to download youtube playlist for a user.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/planetsoni/youtubeplaylistdownloader",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: <TO_BE_DETERMINED>",
        "Operating System :: OS Independent",
    ],
    # Dependent packages (distributions)
    install_requires=["google_auth_oauthlib", "google-api-python-client"],
    python_requires='>=3.6',
)
