# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).
 
## [Unreleased] - yyyy-mm-dd
 
### Added

- Add a tkinter GUI for a user-friendly experience
- Add active KeyListener to halt program execution
- Add multiple template matching for bait choice
 
### Changed

- Refactor code to meet MVC standards
- Change **imageprocessor.py** *ObjectDetector* class from using Strategy pattern to Factory pattern
 
### Fixed
 
## [0.3.1] - 2020-07-21
 
### Added

- Add a **CHANGELOG.md**
- Add template matching for *broccoli bait*
 
### Changed
  
- Change *CircleDetectionAlgorithm* to *ObjectDetectionAlgorithm* for inclusion of template matching of baits
- Change *fishing rod* circle detection to more accurate template matching to prevent lapses in detection
 
### Fixed
 
- Fix *State.fishing* ending prematurely due to lapses in *fishing rod* circle detection