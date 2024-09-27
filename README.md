# Post2Page Converter
version 0.1.0 - 9/27/2024

This utility will convert a Post to a Page in Publii 0.46.x

I created this utility to aid in quickly converting posts from Publii before 0.46.x that were used as pages into actual pages in Publii 0.46.x or later.  The utility is written in Python 3.x.  It is a GUI application using the TKinter library (as ugly as that is).  I have created an executable for the windows environment that can be downloaded here.
On the MacOS or Linux operating system execute the tool using it as a Python script.

## How to Use Post2Page Converter

**Always backup your site before converting posts to pages.**

1. Open the application on your system (or execute it as a Python script from the command prompt).

![figure 1](https://github.com/user-attachments/assets/ac5ab446-e331-44f7-b55d-4fd776b1fd43)

2. click "Select site" and navigate to where your Publii folder stores sites (usually c:/users/User_Dir/Publii/sites).  Select the top-level folder for a site (shown below).

![figure 2](https://github.com/user-attachments/assets/64d52d8b-a067-4f98-97da-996c76c3c50b)

3. The utility will run several checks to make sure your site is ready to convert posts to pages.  First it will connect to the SQLite database which confirms that the folder does is indeed a Publii site.  Next it checks to see what your current theme is.  Next it checks the theme's config.json file to make sure it supports PAGES.  Finally it checks to see if there are one or more posts that are in Published or Draft status and are not already a page.  The figure below shows the tool trying to access a site with a current theme that does not support Pages.

![figure 3](https://github.com/user-attachments/assets/c8c69578-5abe-4157-9dd1-7b1fc3a25350)

4. Once all the checks succeed the tool will list all posts that are not alredy pages.  Select the one you want to convert to a page.

![figure 4](https://github.com/user-attachments/assets/ed470fa2-7c27-47ca-ae65-5a4b13062b89)

5. The post details will be displayed and a button to convert it to a page will be added to the interface as shown below.

![figure 4a](https://github.com/user-attachments/assets/8abb09e5-3d34-4e52-ab69-580b7f095889)

6. Click the button "Convert to Page" to begin the process.  You will be asked if you are sure.

![figure 4b](https://github.com/user-attachments/assets/4eb39d39-163c-4a62-b2b5-cb5e3c8e23e6)

7. Confirm that you are sure and the page will be converted.

![figure 4c](https://github.com/user-attachments/assets/3ffbb461-c8df-4f7f-a09f-1737b5ff1535)

###Warning:

If you are converting a post from a version of Publii before 0.46 that is acting as the homepage for your site (as shown below) open Publii and set this setting (Theme -> Custom Settings -> Layout -> Homepage display) back to "Latest Posts".

![figure 5](https://github.com/user-attachments/assets/ffabc606-ff68-4c9c-a906-71f6889e00ae)

After converting that post to a Page set it to your new homepage (as shown below) in Site Settings -> Advanced Options -> SEO -> Homepage.

![figure 6](https://github.com/user-attachments/assets/7c5213a4-eda6-4448-b721-d07d51347b5f)

## Warnings and License

**WARNING: It is not required to close Publii when converting posts to pages but I highly recommend it.**

Licensed MIT.  The author assumes no responsibility for issues, problems, lost data, etc for using this tool.  Backup you site first!





