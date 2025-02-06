# Fileo

This application is about the files, your files.

Fileo[fɑɪlɔ] - could be FileOrganizer, but that doesn't matter.

The graphical interface is shown in the image below.

![fileo](https://github.com/Michal-D4/fileo/raw/main/img/fileo.jpg)

## The GUI elements:

1. application mode, it determinates how files in the list (8) is selected.
2. the button to display menu to hide/show the widgets("Folders", "Tags", "File Extensions", "Authors") on the left pane.
3. Describes how the list of files (8) was created.
4. buttons related to the file list (8):
   * ![recent](https://github.com/Michal-D4/fileo/raw/main/img/recent.png) - show list of recent files
   * ![search](https://github.com/Michal-D4/fileo/raw/main/img/search.png) - search files by name,
   * ![fields](https://github.com/Michal-D4/fileo/raw/main/img/more.png) - selecting the columns that will be visible in the file list
5. a group of buttons for working with the folder tree: previous-next folder in the history of visited folders; show hidden folders; collapse all branches - expand the last branch if all branches were collapsed.
6. left toolbar, it contains the following buttons from top to bottom:
   1. menu button
   2. switch to "DIR" mode, the file list displays files from the current folder
   3. switch to the "FILTER" mode, the file list displays files according to the filter settings
   4. open filter settings dialog, switch to "FILTER_SETUP" mode
   5. hide/show left pane
7. the folder tree window
8. the file list window
9. panel for displaying/editing file data: notes, tags, authors (for books), file locations (file can be located in several folders)
10. current database name, click on it to enter list of available databases
11. folder tree branch from root to current folder
12. the current file in file list
13. the name of the file whose note is open in the editor, this is not displaying if no note is edited, click here to go to this file and the folder containing this file
14. number of files in the file list

The application works in three main modes: DIR, FILTER and FILTER_SETUP.
* In DIR mode, files are selected by the current directory in the "Folders" widget.
* In FILTER mode, files are selected according to the parameters choosen in the FILTER_SETUP dialog.
* In FILTER_SETUP mode. The filter setup dialog is openning, the file list is changing only by clicking the "Apply" or "Done" button.

There are three additional application modes: RECENT_FILES, FOUND_FILES and FILE_BY_REF.
* RECENT_FILES - list of files you've recently done something with
* FOUND_FILES - list of files you found using the search dialog
* FILE_BY_REF - the file list window contains a file referenced from the note of some file. The transition to this mode occurs after clicking on the link.

In FILTER mode, the list of files depends on the filter options set in FILTER_SETUP mode. The filter may depend on the selected folders, selected tags, and selected authors in the boxes in the left pane. In FILTER_SETUP mode, the list of files does not change when changing the selected folders, tags, authors. But in FILTER mode, any changes are immediately displayed in the list of files.

## Files

As said, the app is about files. Files have a number of attributes:

1. name
2. path, the user practically does not see it, only by opening the directory or copying the full file name and on the "File Info" page
3. file extension
4. tags
5. rating
6. author(s) - usually for books
7. dates of:
    1. modification
    2. last opening
    3. creation
    4. publication (books)
    5. date of last created/modified note to the file
8. number of file openings
9. size in bytes
10. number of pages - usually for books

## Folders

Folders are not linked to the OS file system. Each folder has 2 attributes that affect its appearance: the number of parent folders (one or more than one) and the hidden status (hidden folders are visible if the hidden folder display mode is enabled):

![image-20250118132817380](https://github.com/Michal-D4/fileo/raw/main/img/show_hidden_folders.png)

The following icons used for folders depending of their attributes:

|                     | Hidden                                                       | Visible                                                      |
| ------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| one parent          | ![one_folder_hide](https://github.com/Michal-D4/fileo/raw/main/img/one_folder_hide.png) | ![one_folder](https://github.com/Michal-D4/fileo/raw/main/img/one_folder.png) |
| two or more parents | ![mult_folder_hide](https://github.com/Michal-D4/fileo/raw/main/img/mult_folder_hide.png) | ![mult_folder](https://github.com/Michal-D4/fileo/raw/main/img/mult_folder.png) |

You can freely create, move, copy and delete folders in the folder tree, the files will remain untouched. The application is designed for files, not folders. Folders are just a tool for organizing access to files. If, as a result of deleting folders, the file is not in any of the folders, you can still find it in several different ways: by filter, by searching by name, by searching by text in notes, among recently viewed files. In the next session this "lost" file will appear in the hidden folder "@@Lost".

You can also *copy/move files from one folder to another*  by dragging *with the left or right mouse button pressed*.

> **Important.** Deleting a folder with only one parent will delete all of its child folders. If a folder has more than one parent folder, it will be removed only from the current parent folder and will remain in the others.

## Folders and files

![Folders](https://github.com/Michal-D4/fileo/raw/main/img/Folders.png)

1. Checkbox. Used to switch the "FOLDERS" widget to "Show hidden folders" mode. The "markdown" folder (2b) is hidden, and the same "markdown" folder (2a) is not hidden and is located in the root (does not have a visible parent folder).
2. A "markdown" folder that has more than one parent folder:  
   a. not hidden folder in the root  
   b. hidden folder in the "GUI" folder
3. hovered folder with the tooltip "verse" different from folder name "rhyme"
4. The current (or selected) folder. You can select multiple folders at once using the Shift or Ctrl keys.
5. The current file "SQLite.md".
6. The "SQLite" tag assigned to the current "SQLite.md" file.

## File duplicates

It may happen that there are duplicate files on your disk. It is highly recommended to delete duplicate files. If you need different versions of a file, consider using a version control system such as Git.

Fileo can find files that are identical in content, but only if these files are added to the same fileo session, or rather to the same database. Fileo works with only one database at a time. You can create a report on duplicate files from the main menu:

![Duplicates](https://github.com/Michal-D4/fileo/raw/main/img/Duplicates.jpg)

After creating the report (if duplicates are detected), you can delete all duplicates at once. But it may be better to remove them manually or delete the selected file in the "Locations" page, since the application may remove not the duplicate file you expected.

## How it works

### How to add files?

There are several methods to add files:

1. Open "Search for files..." dialog with main menu item "Scan disk for files": ![scan_disk_dialog](https://github.com/Michal-D4/fileo/raw/main/img/scan_disk_dialog.png)

2. drag files from the file explorer (or similar application) to the folder in the folder tree.

> **Note**. Scanning the file system can be quite lengthy, so it is performed in a separate thread.
> The red circle in the lower left corner is a sign that the thread is working:
>
> ![image-20230213184306153](https://github.com/Michal-D4/fileo/raw/main/img/image-20230213184306153.png)
>
> Only one background thread can run at a time - this is the design of the application. The user interface is not blocking but you should avoid to perform operation that make changes in the database, for example, drag-drop operations. But you can change the list of files by changing a current folder or filter, or you can open files.

3. You can export the selected files (with all their attributes) from the database using the context menu of the file list:

   ![export-files](https://github.com/Michal-D4/fileo/raw/main/img/export-files.jpg)

   and then import them to another database

   ![import-files](https://github.com/Michal-D4/fileo/raw/main/img/import-files.jpg)

   to the folder "New folder" in this case.

   > **Note**. In the file note you can have reference(s) to another file(s) in the data base. If you drag the file with such note the reference will be broken, there is no interbase references.

### How to work with filters

First you should setup the filter:

![image-20230213185910924](https://github.com/Michal-D4/fileo/raw/main/img/image-20230213185910924.png)

With the filter set in the picture, the list of files will include files from the any of `DB`, `ML` or `Rust` folders that have at least one of the `Math`, `ML` or `package` tags, have a rating higher than 4 and were opened on or after `2022-09-14`.

> **Note.** In case "Date of before" &mdash; on or before `2022-11-14` in the case shown in the image.

The Apply button applies a specified filter without closing the Filter Setup dialog box.

The Done button applies the filter, closes the dialog, and switches the application to "**Filter Mode**". In this mode, when you change the selection in any of the fields on the left panel (Folders, Tags, Extensions, Authors), the file list will immediately change accordingly.

### Search files by name

![image-20230428203253627](https://github.com/Michal-D4/fileo/raw/main/img/find_file.jpg)

Search dialog is opened by clicking button ![search](https://github.com/Michal-D4/fileo/raw/main/img/search.png) - search files by name or by shortcut `Ctrl-F`.

The search is performed by pressing the Enter key. "Aa" is a case sensitive search, if checked, "ab" - full word match.

### Search files by text in notes

![search-in-notes](https://github.com/Michal-D4/fileo/raw/main/img/search-in-notes.jpg)

Search dialog is opened by clicking button ![search](https://github.com/Michal-D4/fileo/raw/main/img/search.png) - search files or by shortcut `Ctrl-Shift-F`.

The available options are

- regular expression,
- case sensitive,
- match full word.

The regular expression and match full word options are mutually exclusive. 

### How to make notes to the file

![fileo-comments](https://github.com/Michal-D4/fileo/raw/main/img/file-notes.jpg)

1. "+"  plus button - add new note and open it in the editor
8.  the button to collapse all notes
3. start editing of the note
4. "x" button - delete the note
5. external (http) reference, can be open in the system web browser

#### Note editor

![edit-comment](https://github.com/Michal-D4/fileo/raw/main/img/edit-comment.jpg)

1. the button to save changes, save changes and close editor
2. the button to discard changes

> pressing any of these buttons closes the editor

Note is a markdown and HTML text. Here you can insert *web links*, *links to files registered in the application* (in the current DB), as well as *files from the OS file system*. All this can be done using the drag-drop method.

To display notes the [QTextBrowser](https://doc.qt.io/qt-6/qtextbrowser.html) is used. It supports limited HTML and markdown capabilities. For example, I have to use HTML syntax to display table in this browser:

![note_editor](https://github.com/Michal-D4/fileo/raw/main/img/note_editor.jpg)

Here's how it appears in the note:

![note-with-tabl](https://github.com/Michal-D4/fileo/raw/main/img/note-with-tabl.jpg)

### Tag selector

![tag-selector](https://github.com/Michal-D4/fileo/raw/main/img/tag-selector.jpg)

1. The list of tags associated with the current file. You can input here a list of tags separated by commas. *It is the only place where the new tag can be created.* The new tags will appear in the list 2 and 4.
2. The list of tags. The tags selected in this list apply to the file filter.
3. The context menu in the list of tags. Selected tags are highlighted ('Linux' and 'package'). The tag  'package' is a current tag (last selected).
4. The tag selector. The tags selected here will appear in the list 1.

### Author selector

![author-selector](https://github.com/Michal-D4/fileo/raw/main/img/author-selector.jpg)

1. The list of authors associated with the current file. You can input here a list of authors separated by commas (in square brackets if author name contains comma as in "Vaughan, Lee", otherwise it may be entered without brackets, but new authors without brackets must be in the end of list). It is the only place where the new author can be created. The new authors will appear in the list 2 and 4.
2. The list of authors. The authors selected in this list apply to the file filter.
3. The context menu in the list of authors. The current tag is highlighted - "Vijay  Pande" in this case.
4. The author selector. The authors selected here will appear in the list 1.

### Locations

The file may be located in different folders. In fact, these are links to the same file[^1] in different folders. The file location is represented as a branch of folders from the root folder to the folder in which the link to the file is saved.

![Locations](https://github.com/Michal-D4/fileo/raw/main/img/Locations.jpg)

1 - list of branches where the current file can be found. The list also includes duplicate files, if any. Duplicates are marked with "`----> Dup:`" followed by the name of the duplicate; a duplicate file may have a different name than the file itself; duplicates are identified by having the same content (by a hash computed from its content).

The branch marked with a bullet is ***a current location***.

2 - a context menu:

1. copy - copy selected lines
2. go to this location - go to the file in the folder under mouse cursor
3. Reveal in explorer - show file in explorer
4. delete file from this location - in fact the link to the file is removed from the folder under the mouse cursor, the file itself remains intact
5. Remove duplicate file - the file under mouse cursor will be removed to the trash bin if duplicate of the file exists
6. Select All

3 - the current branch "`SVG>to have 2 folders`"

4 - the current file selected in the file list "`angle_down_20221002213631.svg`"

[^1]:with one exception, the file may be duplicated, i.e. there may be more than one file with the same content.
### File info

![file-info](https://github.com/Michal-D4/fileo/raw/main/img/file-info.jpg)

You can copy file information here by pressing Right mouse button or Right mouse button with Shift.

The "File rating" and "Pages" can be edited here. But they also can be edited directly in the file list if visible:

![file-list-fields](https://github.com/Michal-D4/fileo/raw/main/img/file-list-fields.jpg)

1. The file list
2. Menu to select fields visible in the file list. The checked fields are visible, the field "File Name" is always visible.

### File operations



![file_context_menu](https://github.com/Michal-D4/fileo/raw/main/img/file_context_menu.png)

Almost all operations with files are shown in the context menu on the picture.

Besides them you can copy / move files from one folder to another.

You can also open files by double clicking on "File name". If the file is executable, it will be executed, not opened. Thus, the application can be used as a "Start Menu", it can be even more convenient than the standard "Start Menu".

> **Note:** If you delete a file from a folder, the file will still remain in the DB, even if you delete it from all folders, it can be found by searching by name or part of the name, or using a filter, or at least it will appear in (hidden) folder "@@Lost".
> If you delete a file from the DB, it will be deleted from all folders, and all notes for this file and its links to tags and authors will be lost.

***

### DB selector

All application data is stored into a data base (SQlite DB). The SQlite data base is a single file, you can create as many DB files as you want. All manipulation with the DB files are performing in the DB selector:

![DB-selector](https://github.com/Michal-D4/fileo/raw/main/img/DB-selector.jpg)

The DB can be opened in the current window by double click on the line in the DB list, or select with keyboard up and down arrows key and choose with "Return" key, not "Enter" key on numeric keyboard.

## Color themes

Three color themes have been created for the application: “Default”, “Light” and “Dark”.

You can switch theme in the preferences menu item:

![image-20240505145226631](https://github.com/Michal-D4/fileo/raw/main/img//preferences_in_main_menu.png)

![image-20240505145706247](https://github.com/Michal-D4/fileo/raw/main/img//color_themes.png)

# Installation

* Windows. Download the installer `fileo_setup.x.y.z.exe`  from [sourceforge](https://sourceforge.net/projects/fileo/) where `x.y.z` - version and run it.



* Linux and Windows
  install as Python package from PyPi:

  ```
    > pip install md2fileo
  ```
  and then run with
  ```
    > python -m fileo
  ```
