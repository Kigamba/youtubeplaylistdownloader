# Copyright 2020 Krunal Soni
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import importlib
import os
import sys

# We cannot use relative path to import main module
# since current module name is  __main__
# (We cannot do 'from . import main')
#
# We cannot use relative path without .
# because test framework loads these clases with package name
# (We cannot do 'import main')
#
# We have to use absolute package path, however project path is not included
# in sys.path when running the app with `python youtube_playlist_downloader`
#
# So let's add project path to sys.path and use abosolute import
# so that other modules could use relative path to import

project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_path)
main_mondule = importlib.import_module("youtube_playlist_downloader.main")
main_mondule.main()
