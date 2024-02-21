# Known issues

Two issues related to Linux. I am not going to solve them because Linux is mostly command line OS and there is many different [Linux distributions](https://en.wikipedia.org/wiki/List_of_Linux_distributions) and window managers (choice problem).

1. I haven't packaged app to deploy in Linux, you may install it from PyPi.

2. I couldn't set an app icon in Linux, Fedora, Wayland.

3. Using QLockFile. The disadvantage is that once the original instance is closed, there will be no restrictions on starting new instances. This is not a problem if only one instance is allowed. A local HTML server does not have this drawback. But LockFile is more lightweight solution.
