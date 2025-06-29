# Change Log

## 1.3.49 - 2025, 28 June
* Folder History: Now you can select a folder from the history list.
* Removed instance control. I don't see the need for it.
* some other changes, improvements and bug fixes

## 1.3.48 - 2025, 09 June
* Add the ability to create new file(s) from within the app. The app creates a blank file. It may not be opened by an app that requires a special file format, such as a PDF file.
* some other changes, improvements and bug fixes

## 1.3.46 - 2025, 31 May
* quick fix, filter setup bug - when notes date were not selected.
* Dialogue: "About the program", "Report duplicate files", "Settings", "Scan disk for files" should not open more than one main window.
* Filter setup dialog, if accidentally moved out of main window, shold be opened next time inside main window.

## 1.3.45 - 2025, 30 May
* quick fix, filter must show all files if no option is selected

## 1.3.44 - 2025, 29 May
* Filter files by note creation and modification dates
* fixed bug in qss handling
* downgraded to PyQT6 6.7.3 from PyQT6 6.9.0. PyQT6 since 6.8.0 has problem in TreeView qss
* some other changes and improvements

## 1.3.43 - 2025, 24 May
* set authors for all selected files at once
* save file addition date to DB
* context menu on "File info" tab

## 1.3.42 - 2025, 13 May
* Fixed bug with checking for updates.
* Now checking for updates can be performed automatically when the application is launched if the corresponding flag is set in the preferences.

## 1.3.41 - 2025, 11 May
* I decided not to extract author names from pdf files. The AUTHORS widget can now be used to store any data and will work similarly to tags, i.e. items can be used in the file filter. Title of widget may be changed/edited with right mouse button click.
* some other changes and improvements

## 1.3.40 - 2025, 07 May
* fix bug with maximize-restore main window. Found in linux
* revise the loading files (including drag from os file system)
* remove predefined @@Lost folder. Now all folders are identical in their properties.
* a new condition has been created in the filter to display files that are not in any folder
![image-20230213185910924](https://github.com/Michal-D4/fileo/raw/main/img/filter_no_dir.png)

## 1.3.39 - 2025, 17 April
* revised folder tree history
* predictable behavior of collapse-expand branch of folder tree button
* fixed maximizing app window issue
* shortcuts for many actions have been created
* fixed saving file list header issue
* revised drag-drop usage
* transition to python 3.13

## 1.3.38 - 2025, 08 April
* fixed error with adding new DB in db list
* button in the DB list to add DB

## 1.3.37 - 2025, 06 April
* Revised folder history

## 1.3.36 - 2025, 02 April
* fix DB list processing in multi-instance mode
* export/import files, including files referenced from notes

## 1.3.35 - 2025, 30 March
* fix not opening DB in new window
* clear filelist when create new DB

## 1.3.34 - 2025, 11 March
* revised folder history processing, walking through folder history

## 1.3.33 - 2025, 08 March
* case insensitive file extensions
* fixed critical error in displaying empty folder tree
* fixed error in viewing folder history.

## 1.3.32 - 2025, 17 February
* Minor change in copying folder tree
* some other minor changes and improvements

## 1.3.31 - 2025, 16 February
* Fixed some issues with restoring the application state on startup.
* Added the ability to copy a folder tree. This can be useful if you plan to reorganize the folder tree.

## 1.3.30 - 2025, 07 February
* some minor changes, aligned top bar along the entire length, README.md, etc.

## 1.3.29 - 2025, 06 February
* fix file search error if template contains comma
* do not open DB on startup if used

## 1.3.28 - 2025, 05 February
* Revised saving of settings between sessions.
* Fixed a several bugs based on testing results on a clean Linux system.
* fileo.AppImage created for Linux deployment.

## 1.3.27 - 2025, 27 January
* Human readable file size
* Copy information from the "File info" tab to the clipboard
    * with press Right mouse button to copy current line
    * with press Right mouse button + Shift to copy everything

## 1.3.26 - 2025, 25 January
* fix issue when saving/restoring file list header
* drag-drop multiple files into a note from the OS file system and from the application's file list
* change README.md

## 1.3.25 - 2025, 23 January
* Removing broken links in folder history after user deleted folders.
* Some changes in README.md

## 1.3.24.1 - 2025, 19 January
* fix issue with displaying/saving notes for recently added files. App crashes and can't be restarted.

## 1.3.24 - 2025, 18 January
* fix color theme switching issue
* fix the connection between notes and files in case of file duplication; it is strongly recommended to delete duplicates
* new set of icons for dir tree items
* revise README.md, the session related to folder description
* some other changes and improvements

## 1.3.23 - 2024, 31 December
* fix file list header issue
* Some other code changes

## 1.3.22 - 2024, 28 December
* fix some file search issues

## 1.3.21 - 2024, 26 December
* file search by text in notes
* Some other code changes and improvements

## 1.3.20 - 2024, 21 December
* set tags for all selected files at once, remove only for the current file, as before
* warning that files may not be immediately visible if you drag them into a folder from Explorer while the app is in Filter mode
* Some other code changes and improvements

## 1.3.19 - 2024, 17 December
* fix html code usage in notes
* fix first note height issue
* Some other code changes and improvements

## 1.3.18 - 2024, 17 December
* fix color theme switching issue
* fix issue with folder history format
* Some other code changes and improvements

## 1.3.17 - 2024, 14 December
* fix issue with reading configuration when the application is in a frozen state.

## 1.3.16 - 2024, 14 December
* remake folder history, folder can appear in history only once
* fix some issues with showing notes
* fix some issues on startup

## 1.3.15 - 2024, 08 December
* To create a new instance of the application, the "first_instance" parameter is explicitly defined.
* When creating a new instance, the window is positioned relative to the current one.

## 1.3.14 - 2024, 06 December
* repair opening new window from DB list
* update tag and author lists when drag-drop or import files
* Some other code changes and improvements

## 1.3.13 - 2024, 04 December
* repair call of file switching handler; issue with QT currentChanged QTreeView event; currentRowChanged selectionModel signal is used instead.

## 1.3.12 - 2024, 01 December
* prevent reopening same DB in the new instance of application

## 1.3.11 - 2024, 23 November
* fix codeblock show issue

## 1.3.10 - 2024, 20 November
* themes with big font
* Some code changes and improvements

## 1.3.09 - 2024, 11 November
* new option in the filter - "all subfolders"

## 1.3.08 - 2024, 07 November
* fix some tag/author selector and editor issues

## 1.3.07 - 2024, 01 November
* fix note color and collapse issue when changing color theme

## 1.3.05 - 2024, 30 October
* fix note height issue when changing color theme

## 1.3.04 - 2024, 19 September
* the readme file corrected
* Some code changes and improvements.

## 1.3.03 - 2024, 02 September
* fix issue with folder creation
* fix issue with folder name editing
* Some code changes and improvements.

## 1.3.02 - 2024, August 21

* Fix issue find when install in the Linux.
* ToolTip to folder is saved only if it differs from the folder name.
* App icon in the about dialog.

## 1.3.01 - 2024, August 14

* Revise template of color themes. Only one template is in use: "default.qss", and 3 themes: "Default", "Dark1" and "Dark2", that defined by .param files.
* Specify color of HTML links in file notes.
* ToolTip to folder is editable now.
* Some other code changes and improvements.

## 1.2.01 - 2024, May 05

* Three color themes have been created for the application: “Default”, “Light” and “Dark”.
* several other changes and improvements to the code

## 1.1.08 - 2024, March 01

* use Inno Setup yo make Windows Installer instead of InstallForge.
* implement the duplicate removal on the "Locations" page. This allows to choose a particular file to delete, but only if that file has duplicates.
* several other changes and improvements to the code

## 1.1.07 - 2024, February 21
* managing duplicate files. It is not recommended to have multiple files with the same content. Now you will not be able to open a file from an application if it has a duplicate registered in the same database.
Now you can remove all duplicates from the application at once. But it may be better to remove them manually, since the application may remove not the duplicate file you expected.
* Notes for a file can be saved as a separate Markdown file. Old notes are deleted and one new note is created with a link to the file containing the saved notes.
* several other changes and improvements to the code

## 1.1.06 - 2024, February 06
* sort database list in order of last used first
* You can now select a database using the arrow keys on your keyboard and pressing the "Return" key, often labeled "Enter" on the keyboard.
* several other changes and improvements to the code

## 1.1.05 - 2024, February 02
* define directory "~/.local/share/fileo" for app data in Linux. In windows it is '%LOCALAPPDATA%/fileo".
* change the project name. The old name is “md4_fileo”, the new one is “md2fileo”. The goal is to avoid underscores and hyphens. PyPi converts underscores to hyphens; a module with that name is difficult to import. PEP 8 says "Modules should have short, all-lowercase names. Underscores can be used in the module name if it improves readability. Python packages should also have short, all-lowercase names, *although the use of underscores is discouraged*".

## 1.1.04 - 2024, February 02
* remove the pywinauto package from dependencies. It conflicts with PyQt. It was used for a single purpose only: in single instance mode to activate an existing instance when trying to open a second instance. Now this existing instance will not display in the foreground when you try to open a second instance. I was going to remove this package anyway because it is too big to be used for this sole purpose.

## 1.1.03 - 2024, January 30
* frameless main window also in Linux
* fix some issues with move-resize main window. Everything seems to be running smoothly now
* many other changes and improvements in the code

## 1.1.02 - 2024, January 17
* shortcuts for the most common actions: creating (Ctrl-W, Ctrl-E) and deleting (Del) folders, creating (Ctrl-N) and saving (ctrl-S) a note, searching for a file, displaying file history, renaming folders, files, tags, authors with F2 key.
* show the beginning of the note in the note header

## 1.1.01 - 2024, January 14
* created a report on files with the same names
* removed Awesome icon font, using SVG icons instead. Due to this, the size of the application has been reduced by more than 5 MB.
* fixed a bug in sorting the list of files by file name: comparing the name and extension separately, and not as one string
* many other changes and improvements

## 1.0.08 - 2023, December 20
* replace spaces in href with %20 to make links work.
* fix bug with switch from filter setup to filter to show filtered files.

## 1.0.07 - 2023, December 17
* fix bug with maximize/restore icons
* draw border around the filter setup dialog
* set current date in the filter setup dialog if default is 'Sep 14 1752'

## 1.0.06 - 2023, December 17
* fix little bug with drag move files
* some user interface and code enhancements

## 1.0.05 - 2023, December 16
* fix bag with empty DB

## 1.0.04 - 2023, December 15
* toggle instance control with toml file
* list of recent files, save between sessions
* insert into note the link to URI (http, file) with drag-drop
* insert into note the link to files registered in db with drag-drop
* open the file/url using the link in the note
* go to the file using the link in the note
* show file duplicates in the Locations tab
* introduce sortRole into fileList model

## 1.0.03 - 2023, November 16
* fixed a bug with sorting the file list by publication date
* allowed drag move from the list of filtered files

## 1.0.02 - 2023, November 14
* sort DB list and many other improvements to the DB selector
* save/restore note editor state between sessions
* improve checking for updates

## 1.0.01 - 2023, November 11
* ResizeMode of the file list columns is set to "Interactive" instead of "ResizeToContents".
  When ResizeMode was set to "ResizeToContents", the column widths changed frequently, which didn't look good. Now the columns width can be changed only by the user and when resizing the file list.
* removed many app global variables that were defined in app_globals.py

## 1.0.0 - 2023, November 08
* check for updates from the menu

## 0.9.57 - 2023, November 05
* Fixed a bug in the file filter. It was returning all the files when they shouldn't be.

## 0.9.56 - 2023, November 01
* displaying widgets in the bottom panel of the file list in a uniform visual style
* move file tags methods to file_tags.py module
* stop the instance management thread when all instances are closed, even if some of them crashed
* refactor managing of file list columns
* some changes to clean up the code

## 0.9.55 - 2023, October 16
* fix bags found in Linux
* It turned out that in Linux (Fedora, Wayland window system) it is impossible to move and resize a frameless window. All Linux systems now use a standard main window with a title bar.
* enable/disable logging in the preferences menu
* open new window in a frozen state from main menu and DB chooser context menu
* some changes to clean up the code

## 0.9.54 - 2023, October 04
* fix issue: the search for lost files thread interrupts user actions
* make it possible to move files when dragging from the list of found files
* fix bug: dragging files from file system adds folders if selected
* fix a bug: in the "any tag" filter the tag is ignored if only one tag is selected

## 0.9.53 - 2023, September 25
* fix error in connection to socket in Linux, when server not started the exception is
"`Connection refuse`", not "`socket.timeout`"
* fix bug in `load_files` module, function `get_dir_id` needs parameter of Path type, not `str`
* in Filter mode with single folder selected, files are drag-dropped in the same way as in Dir mode, i.e. move is also available
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
