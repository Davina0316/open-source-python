# Gmail Client Interface
This interface defines the behaviour of the Gmail Client, including how the client should connect/disconnect to Gmail, and the functionalities of the client such as reading, sending, deleting, and marking emails. This Gmail Client will later be intergrated with other teams' project such as AI Converstion Client, Chat Client or Issue Tracker Client.

---

## Scope of Project
This project is to develop a gmail client that can perform the following actions:
- Connect to gmail server.
- Login/Logout using address and password provided by user.
- Authenticate itself with OAuth token.
- Send email.
- Select a mailbox from a list of mailboxes, get the emails in the mailbox, mark them as read or delete them.

Example of some **out-of-scope** functionalities are:
- Replying emails.
- Mark emails as spam.
- Unsubscribe email promos.
- ...

## Interface Definition

1. ```connect(self) -> bool```
   - **Description**: Establish a connection to the Gmail server or service.
   - **Parameters**:
     - **self**: Instance of the Gmail client.
   - **Returns**:
     - `True` if the connection is successfully established.
     - `False` otherwise.

2. ```login(self, username: str, password: str) -> bool```
   - **Description**: Log in to the Gmail account using the provided username and password.
   - **Parameters**:
     - **self**: Instance of the Gmail client.
     - **username** *(str)*: The user’s Gmail address.
     - **password** *(str)*: The user’s password.
   - **Returns**:
     - `True` if the login is successful.
     - `False` otherwise.

3. ```authenticate(self, username: str, access_token: str) -> bool```
   - **Description**: Authenticate using an OAuth access token instead of a password.
   - **Parameters**:
     - **self**: Instance of the Gmail client.
     - **username** *(str)*: The user’s Gmail address.
     - **access_token** *(str)*: The OAuth access token.
   - **Returns**:
     - `True` if the authentication is successful.
     - `False` otherwise.

4. ```logout(self) -> None```
   - **Description**: Log out from the current Gmail session.
   - **Parameters**:
     - **self**: Instance of the Gmail client.
   - **Returns**:  
     - Nothing (`None`). This method terminates the active session.

5. ```fetch_mailboxes(self) -> list[str]```
   - **Description**: Retrieve a list of available mailboxes (labels) in the Gmail account.
   - **Parameters**:
     - **self**: Instance of the Gmail client.
   - **Returns**:
     - A `list[str]` containing the names of all available mailboxes/labels.

6. ```use_mailbox(self, mailbox: str) -> bool```
   - **Description**: Select the specified mailbox (label) to operate on.
   - **Parameters**:
     - **self**: Instance of the Gmail client.
     - **mailbox** *(str)*: The name of the mailbox to select.
   - **Returns**:
     - `True` if the mailbox was successfully selected.
     - `False` otherwise.

7. ```get_emails_list(self) -> List[Dict]```
   - **Description**: Fetch a list of emails (in the currently selected mailbox).
   - **Parameters**:
     - **self**: Instance of the Gmail client.
   - **Returns**:
     - A `List[Dict]` where each dictionary contains metadata such as 
       `subject`, `sender`, `snippet`, etc.

8. ```get_email_content(self, email_id: str) -> Dict```
   - **Description**: Retrieve the full content of a specific email.
   - **Parameters**:
     - **self**: Instance of the Gmail client.
     - **email_id** *(str)*: Unique identifier of the email to be fetched.
   - **Returns**:
     - A `Dict` containing detailed information about the email (e.g., headers, body, attachments).

9. ```send_email(self, to: str, subject: str, body: str) -> bool```
   - **Description**: Send an email to the specified recipient with the given subject and body.
   - **Parameters**:
     - **self**: Instance of the Gmail client.
     - **to** *(str)*: The recipient’s email address.
     - **subject** *(str)*: The subject line of the email.
     - **body** *(str)*: The content/body of the email.
   - **Returns**:
     - `True` if the email was sent successfully.
     - `False` otherwise.

10. ```delete_email(self, email_id: str) -> bool```
    - **Description**: Delete an email by its unique identifier.
    - **Parameters**:
      - **self**: Instance of the Gmail client.
      - **email_id** *(str)*: Unique identifier of the email to be deleted.
    - **Returns**:
      - `True` if the email was deleted successfully.
      - `False` otherwise.

11. ```mark_as_read(self, email_id: str) -> bool```
    - **Description**: Mark an email as read by its unique identifier.
    - **Parameters**:
      - **self**: Instance of the Gmail client.
      - **email_id** *(str)*: Unique identifier of the email to be marked as read.
    - **Returns**:
      - `True` if the email was marked as read successfully.
      - `False` otherwise.