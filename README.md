# Fileo

This application is about the files, your files.

Fileo[fɑɪlɔ] - could be FileOrganizer, but that doesn't matter.

The graphical interface is shown in the image below.

![fileo](https://github.com/Michal-D4/fileo/raw/main/img/fileo.jpg)

## The GUI elements:

1. The label to display application mode
2. the button to display menu to hide/show the widgets("Folders", "Tags", "File Extensions", "Authors") on the left pane. All menu items checked in the image &ndash; this means that all widgets are visible.
3. the name of current file
4. buttons to search files by name and to select which fields will be visible in the file list
5. the group of buttons for working with the tree of folders
6. the left toolbar, it contains the following buttons from top to bottom:
   1. button to chose/create the data base file
   2. selection of the "DIR" mode of application, the file list shows the files from the current folder
   3. selection of the "FILTER" mode, the list of files shows the files according to the filter settings
   4. open the filter settings dialog, switch application into "FILTER_SETUP" mode
   5. open dialog to scan the file system to load files into the database
   6. hide/show left pane
   7. menu button
7. the list of files from selected folder, of created by filter
8. the name of the current database
9. the branch of folder tree from the root to the current folder
10. the panel to show/edit file data: comments(notes), tags, authors(for books), locations - the folder branches where the current file can be found - file may reside in the several folders.

The application works in three main modes: DIR, FILTER and FILTER_SETUP. In DIR mode, files are selected by the current directory in the "Folders" widget.

In the FILTER mode, the list of files depends on the parameters of the filter set in FILTER_SETUP mode.

## How it's done

As said, the app is about files. Files have a number of attributes:

1. name
2. path, the user will almost never see it, only by opening a directory or copying the full filename and in the "File info" page
3. extension
4. tags
5. rating
6. author(s) - usually for books
7. dates
   1. modified
   2. opened
   3. created
   4. published (books)
8. rating
9. how many times the file has been opened
10. size
11. pages - usually for books

The following attributes are used in filter: all dates (but only one can be used at a time), extension, tags, rating, authors, and folder which was intentionally not included in the file attributes.

Folders are not associated with file system directories, the path is used for that. You can freely create, move, copy and delete folders in the folder tree, the files will remain intact. You can, for example, create multiple folder hierarchies, this can be handy. Of course, if you delete all folders it will be impossible to access files using folder tree, but they remain accessible by filter. The next time the **`@@Lost`** folder will appear, it can be used to access files that are not in any other folder.
You can also copy/move files from one folder to another. **Copying** is carried out by dragging *with the left mouse button pressed*, **moving** - *with the left mouse button and Shift key pressed*.

## How it works

### How to add files?

There are two method to add files:

1. Open "Search for files..." dialog with the button ![image-20230210145215938](https://github.com/Michal-D4/fileo/raw/main/img/image-20230210145215938.png)

   ![image-20230210145404623](https://github.com/Michal-D4/fileo/raw/main/img/image-20230210145404623.png)

2. drag files from the file explorer (or similar application) to the folder in the folder tree.

> **Note**. Scanning the file system can be quite lengthy, so it is performed in a separate thread.
> The red circle in the lower left corner is a sign that the thread is working:
>
> ![image-20230213184306153](https://github.com/Michal-D4/fileo/raw/main/img/image-20230213184306153.png)
>
> Only one background thread can run at a time - this is the design of the application. The user interface is not blocking but you should avoid to perform operation that make changes in the database, for example, drag-drop operations. But you can change the list of files by changing a current folder or filter, or you can open files.

3. You can export the selected files (with all their attributes) from one database using the file list context menu

   ![export-files](https://github.com/Michal-D4/fileo/raw/main/img/export-files.jpg)

   and then import them to another database

   ![import-files](https://github.com/Michal-D4/fileo/raw/main/img/import-files.jpg)

   to the folder "New folder" in this case.

### How to work with filters

Firstly you should setup the filter:

![image-20230213185910924](https://github.com/Michal-D4/fileo/raw/main/img/image-20230213185910924.png)

With filter defined on the picture the file list will include files from folders `DB`, `ML` and `Rust`, that has at least one of tags `Math`, `ML` or `package`, has rating greater than 4, and opened after `2022-09-14`.

> **Note** Here "after" and "before" include the date in the input fields 2022-09-14 and 2022-11-14. That is, if "after"and "before" are equal then the filter includes files with a date equal to this date.

The Apply button applies a specified filter without closing the Filter Setup dialog box.

The button Done applies a filter, closing dialog and switch application into "Filter mode". In this mode when you change selection in one of the widgets in the left pane (Folders, Tags, Extensions, Authors) the list of files is changing accordingly.

### How to find files by name

![image-20230428203253627](https://github.com/Michal-D4/fileo/raw/main/img/find_file.jpg)



### How to make notes to the file

![fileo-comments](https://github.com/Michal-D4/fileo/raw/main/img/fileo-comments.jpg)

1. "+"  plus button - add new note and open it in the editor
6. "x" button - delete the note
8.  the button to open the note in the editor

#### Note editor

![edit-comment](https://github.com/Michal-D4/fileo/raw/main/img/edit-comment.jpg)

1. the save changes button
2. the button to discard changes

Note is a markdown text.

### Tag selector

![tag-selector](https://github.com/Michal-D4/fileo/raw/main/img/tag-selector.jpg)

1. The list of tags associated with the current file. You can input here a list of tags separated by commas. It is the only place where the new tag can be created. The new tags will appear in the list 2 and 4.
2. The list of tags. The tags selected in this list apply to the file filter. 
3. The context menu in the list of tags. The current tag is highlighted - "package" in this case.
4. The tag selector. The tags selected here will appear in the list 1.

### Author selector

![author-selector](https://github.com/Michal-D4/fileo/raw/main/img/author-selector.jpg)

1. The list of authors associated with the current file. You can input here a list of authors separated by commas (in square brackets if author name contains comma as in "Vaughan, Lee", otherwise it may be entered without brackets, but new authors without brackets must be in the end of list). It is the only place where the new author can be created. The new authors will appear in the list 2 and 4.
2. The list of authors. The authors selected in this list apply to the file filter. 
3. The context menu in the list of authors. The current tag is highlighted - "Vijay  Pande" in this case.
4. The author selector. The authors selected here will appear in the list 1.

### Locations

![Locations](https://github.com/Michal-D4/fileo/raw/main/img/Locations.jpg)

The current file "Environment Variables in Linux.md" has 5 locations (Paths/Folder Tree branches).

The letters "C" and "H" in brackets means "Copy" and "Hidden". "Copy" and "Hidden" are attributes of folder. For example, the folder "fileo" in the path 2 is a copy of the folder "fileo" in the path 1; the folder "Linux" is "Hidden", but it is shown in the picture below because of the "FOLDERS" widget is in "Show hidden folders" mode:

![Folders](https://github.com/Michal-D4/fileo/raw/main/img/Folders.jpg)

1. The "FOLDERS" widget
2. The check box. It is used to switch the "FOLDERS" widget to the "Show hidden folders" mode. The folders "@@Lost" and "Linux" are hidden; "fileo" and "New folder1" in the folder "New folder2" are copies. The only difference between folder and its copies is that when you delete folder all its copies and all its children will be deleted too, whereas deletion of any copy of folder does not impact any other folder.
3. The current file. "Environment Variables in Linux.md"

### File info

![file-info](https://github.com/Michal-D4/fileo/raw/main/img/file-info.jpg)

The "File rating" and "Pages" can be edited here. But they also can be edited directly in the file list if visible:

![file-list-fields](https://github.com/Michal-D4/fileo/raw/main/img/file-list-fields.jpg)

1. The file list
2. Menu to select fields visible in the file list. The checked fields are visible, the field "File Name" is always visible.

