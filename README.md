# Udacity Full Stack Web Developer Nanodeegree
## Project: Multi_User_Blog

This is a web site that has the purpose of being a muulti user blog.

## PROJECT SPECIFICATIONS
as of July 2016

Code Functionality

| CRITERIA                                     | MEETS SPECIFICATIONS                      |
|----------------------------------------------|-------------------------------------------|
| What framework is used?                      | App is built using Google App Engine      |
| Blog is deployed and viewable to the public. | The submitted URL is publicly accessible. |

Site Usability

| CRITERIA                                                             | MEETS SPECIFICATIONS                                                                                                                                                                    |
|----------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| The signup, login, and logout workflow is intuitive to a human user. | User is directed to login, logout, and signup pages as appropriate. E.g., login page should have a link to signup page and vice-versa; logout page is only available to logged in user. |
| Editing and viewing workflow is intuitive to a human user.           | Links to edit blog pages are available to users. Users editing a page can click on a link to cancel the edit and go back to viewing that page.                                          |
| Pages render correctly.                                              | Blog pages render properly. Templates are used to unify the site.                                                                                                                       |

Accounts and Security

| CRITERIA                                     | MEETS SPECIFICATIONS                                                                                        |
|----------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| User accounts are appropriately handled.     | Users are able to create accounts, login, and logout correctly.                                             |
| Account information is properly retained.    | Existing users can revisit the site and log back in without having to recreate their accounts each time.    |
| Usernames are unique.                        | Usernames are unique. Attempting to create a duplicate user results in an error message.                    |
| Passwords are secure and appropriately used. | Stored passwords are hashed. Passwords are appropriately checked during login. User cookie is set securely. |

Permissions

| CRITERIA | MEETS SPECIFICATIONS |
|------------------|--------------|
| User permissions are appropriate for logged out users. | Logged out users are redirected to the login page when attempting to create, edit, delete, or like a blog post. |
| User permissions are appropriate for logged in users. | Logged in users can create, edit, or delete blog posts they themselves have created.
 Users should only be able to like posts once and should not be able to like their own post. |
| Comment permissions are enforced. |
| Only signed in users can post comments.
Users can only edit and delete comments they themselves have made. |

Code Quality

| CRITERIA | MEETS SPECIFICATIONS |
|----------|----------------------|
| Code should be readable per the Google Python Style Guide. | Code follows the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html). |
| Code is well structured. | Code follows an intuitive, easy-to-follow logical structure. |
| Code is well commented. | Code that is not intuitively readable is well-documented with comments. |

Documentation

| CRITERIA | MEETS SPECIFICATIONS |
|----------|------------------------|
| Are steps for running the project provided in a README file? | Instructions on how to run the project are outlined in a README file. |


### HOW TO RUN THIS PROJECT
#### Install
1) Make sure [python 2.7](https://www.python.org/downloads/) is installed on your computer.  
2) Download and install [Google App Engine SDK for Python](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python)  
3) Download and Extract this .zip file

#### Usage
1) Open the Google App Enginge Launcher  
2) Click on "File" and "Add Existing Application"  
3) Select the folder where extracted just now in your pc.  
4) Click Run  
5) Go to your browser and type in the address "localhost:[port number used]"
