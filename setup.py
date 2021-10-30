from setuptools import setup
python_requires='>=3.8',
install_requires=(
    "django",
    "python-magic",
    "spotipy",
    "mutagen",
    "coloredlogs",
    "unicode-slugify",
    "pytube",
    "bs4",
    "lyricwikia",
    "tqdm",
    "appdirs",
    "PyYAML"
)

setup(
    name='fanch-spotidl',
    version='0.1.0',
    packages=['app', 'spotdl', 'spotdl.encode', 'spotdl.encode.encoders', 'spotdl.lyrics', 'spotdl.lyrics.providers',
              'spotdl.helpers', 'spotdl.metadata', 'spotdl.metadata.embedders', 'spotdl.metadata.providers',
              'spotdl.authorize', 'spotdl.authorize.services', 'spotdl.command_line', 'portail', 'portail.views',
              'portail.migrations'],
    url='',
    license='GPLv3',
    author='fanch',
    author_email='francois@gautrais.eu',
    description='Une application pour automatiser le téléchargement de musique sur youtube'
)
