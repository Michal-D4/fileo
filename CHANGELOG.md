# Change Log

## 0.9.53 - 2023, September 09
* in Filter mode with single folder selected drag-drop files in the same way as in Dir mode
* start new instance with DB selection
* start new instance from menu
* revision to multiple instance management, using sockets
* revision to resizing, showing and hiding file list columns

## 0.9.52 - 2023, September 07
* change app icon format from SVG to ICO. SVG sometimes doesn't work properly
* clear file list when switch to empty DB
* fix bug in creation new DB

## 0.9.51 - 2023, August 25
* fix error in mimetype "text/uri-list"

## 0.9.50 - 2023, August 24
* drag files between app instances
* always store the file path in posix format to avoid duplication of paths
* in case the file has been moved to another directory, provide the option
to open it manually to save the new path
* fix bug in saving file notes at runtime due to duplicate notes reference

## 0.9.49 - 2023, August 04
* had to create 2 new versions to put the homepage in PYPi

## 0.9.47 - 2023, August 02
* fix small bug
* change version to publish in PyPi

## 0.9.46 - 2023, August 02
* change project name to "md4_fileo"
* publish in PyPi

## 0.9.45 - 2023, August 02
* remake "Reveal file in explorer"
* fix bug, duplicating a file note in the list of notes when saving after editing
* fix bug, changing file list fields not working
* customize of existing DB for new app version

## 0.9.44 - 2023, July 31
* the terms "note" and "comment" were used interchangeably,
  currently used only note, Pragma "user_version" is set to 8.
* fix bug with loading file list when switching DB
* fix bug with saving file note: correct credentials are saved in editor

## 0.9.43 - 2023, July 26

* on "Locations" tab:
  * remove file from location
  * navigate to a specific file location
* add possibility to walk through  folders-files and notes to different files while editing the note  to the particular file, and possibility to return to that particular file at any moment
* fix bug with restoring first item in folder history
* some changes to improve and clean up the code (quite a lot)

## 0.9.42 - 2023, July 10

* fix issue with copying note text into editor
* fix bug with collapsed note size
* change the term "folder copy" to "folder link" in code and DB as more suitable

## 0.9.41 - 2023, July 06

* show each comment/note to file in a separated widget. All file note widgets in one container. The previous solution (show all notes in one `QTextBrowser` widget) was fragile, eg. buttons for editing and deleting notes often lost icons.
* fix bug with restoring/saving settings of file list fields
* about dialog. Now can show (F11) python version and the user version of DB (
  see SqLite "`PRAGMA user_version`").
* working with duplicate files: report on duplicates, merging all notes to a file from all duplicates, moving comments when deleting a duplicate file to one of the remaining duplicates, the total number of file openings and the maximum rating of the file.
* fix bug when walking through folder history (next/previous)

## 0.9.4 - 2023, June 15

* single instance - set in Preference dialog
* in case of single instance, activate existing app. screen (in Linux, Windows was done before)
* fix some bugs when the DB didn't open on startup, eg. in the second instance
* fix some bags with folder history

## 0.9.3 - 2023, June 08

* fix problems with collapse/expand the folder tree:
  - collapsed status should be reset if some branch is expanded manually
  - does not restore a collapsed branch on Linux, SQLite issue
* in Linux, drag-drop is always done with the left button and always with the menu, this is the default behavior of a Linux application.
  * in Linux drag-drop without menu if Ctrl or Shift modifiers are used
* fix problem with restoring appMode
* refactoring of working with icons

## 0.9.2 - 2023, June 06

* only one application instance may be started.
  On Windows, when trying start second instance, the first one gets the focus; Linux hasn't implemented this yet.
* copy list of selected filenames with path (full filename) and without path
* fix save/restore folder history bag
* fix SQLite database search for files with non-ASCII characters in the name
