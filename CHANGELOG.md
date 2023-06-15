# Change Log

## 0.9.4 - 15 June, 2023

* single instance - set in Preference dialog
* in case of single instance, activate existing app. screen (in Linux, Windows was done before)
* fix some bugs when the DB didn't open on startup, eg. in the second instance
* fix some bags with folder history

## 0.9.3 - 08 June, 2023

* fix problems with collapse/expand the folder tree:
  - collapsed status should be reset if some branch is expanded manually
  - does not restore a collapsed branch on Linux, SQLite issue
* in Linux, drag-drop is always done with the left button and always with the menu, this is the default behavior of a Linux application.
  * in Linux drag-drop without menu if Ctrl or Shift modifiers are used
* fix problem with restoring appMode
* refactoring of working with icons

## 0.9.2 - 06 June, 2023

* only one application instance may be started.
  On Windows, when trying start second instance, the first one gets the focus; Linux hasn't implemented this yet.
* copy list of selected filenames with path (full filename) and without path
* fix save/restore folder history bag
* fix SQLite database search for files with non-ASCII characters in the name
