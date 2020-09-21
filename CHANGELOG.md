# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

### Added

- Add a tkinter GUI for a user-friendly experience
- Add active KeyListener to halt program execution
- Add grayscale option for *TemplateMatchLocator*

### Changed

- Refactor code to meet MVC standards in GUI implementation
- Improve template matching accuracy for baiting, might use SSIM

## [0.6.1] - 2020-09-21

### Added

- Created prototype of display debugger

### Changed

- Made *HoughCircles* parameters customizable through **cotd.cfg**

## [0.6.0] - Codename: "Ristretto" - 2020-09-19

### Added

- Implemented new *Fisher* class to encapsulate fishing operations
- Added new method of detecting circles/bubbles

### Changed

- Updated *frod* template
- Refactored main codebase for simplicity
- Changed 0.01 sleep time in *windowrapper.click()* method to 0.05

### Removed

- Removed experimental custom bait picks
- Removed templates for *catch_region*
- Removed unnecessary classes in **imageprocessor.py**

## [0.5.0] - Codename: "Macchiato" - 2020-08-01

### Added

- Added new templates for use
- Created **cotd.cfg** to easily modify most parameters without the need to recompile
- Created *ImageDisplay* and *Canvas* in **imageprocessor.py** for the *--debug* parameter
- Implemented display debugger in catch region for *--debug* parameter
- Added a deadlock streak feature to terminate program upon passing set threshold

### Changed

- Updated current image templates to match wedding anniversary templates

### Removed

- Removed parameter (*bait*, *fps*) passing on shell in favor of setting them in **cotd.cfg**

## [0.4.3] - 2020-07-30

### Added

- Created template grabber helper file
- Added bluebait to resources 

## [0.4.2] - 2020-07-29

### Added

- Added experimental singular bait choosing feature
- Added result percentage to tuple in template *find_object()* function

### Changed

- Restored *fix_wpos()* function
- Set template match threshold to 90%, previously 70%
- Refactored code to include addition of result percentage in *find_object()* tuple

## [0.4.1] - Codename: "Milkmocha" - 2020-07-21

### Changed

- Change *algorithm* parameter to *bait*
- Modify bait style implementation in main loop
 
## [0.4.0] - Codename: "Milkmocha" - 2020-07-22
 
### Added

- Add a **CHANGELOG.md**
- Add multiple template matching for *bait* choice
- Add *MinMaxRadiusException*
 
### Changed

- Change **imageprocessor.py** *ObjectDetector* class from using Strategy pattern to Factory pattern
- Rework **imageprocessor.py** to implement Factory pattern to reduce complexity
- Rework **cotd.py** for the introduction of Factory pattern to main file
- Change class name *InvalidWindowCoordinates* to *InvalidWindowCoordinatesException*
- Change **background.jpg** to **catch_region.jpg**

### Fixed

- Fix late outputs to console in executable
- Fix deadlock timer in main loop
 
### Removed

- Remove unmaintained and unused circle detection algorithms
- Remove *algorithm* parameter in program
- Remove unused images in **/res**
- Remove unused **/exceptions** folder

 
## [0.3.1] - Codename: "Latte" - 2020-07-20
 
### Added

- Add template matching for *broccoli bait*
 
### Changed
  
- Change *CircleDetectionAlgorithm* to *ObjectDetectionAlgorithm* for inclusion of template matching of baits
- Change *fishing rod* circle detection to more accurate template matching to prevent lapses in detection
 
### Fixed
 
- Fix *State.fishing* ending prematurely due to lapses in *fishing rod* circle detection