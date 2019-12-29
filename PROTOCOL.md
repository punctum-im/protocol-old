# The Euphony Project

> The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL
> NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and
> "OPTIONAL" in this document are to be interpreted as described in
> [RFC2119](https://tools.ietf.org/html/rfc2119).

## Introduction

The Euphony Project is a chat protocol, inspired by Matrix and Discord. It's fully free and can be implemented by anybody. Servers using the protocol are designed to federate, which allows for multiple self-hosted instances to connect to each other.

The main goal of this project is to create a chat platform that is transparent and easy to implement, while retaining many functions that other software does not have (such as conferences - groups with channels in them).

## Keywords

* User - User of an instance.
* Account - An account on an instance. Only used when mentioning the object type.
* Instance - The instance (running a Euphony Project compatible server).
* Conference - A group which contains channels.
* Channel - A channel of communication. DMs and group chats are also channels.
* Message - A single message, placed in a text channel.

Additional note: all JSON fields that use "..." as the name are intended to be comments and MUST NOT be included in final requests.

### Example keywords

Note: if only one user/instance/conference/action is mentioned in the example, use the full words. Only use these keywords for examples where multiple objects exist.

* Ux - User. The x is a number assigned to each user in the example.
* Ix - Instance. The x is a number assigned to each instance in the example.
* Cx - Conference. The x is a number assigned to each conference in the example.
* Ox - Object. The x is a number assigned to each object in the example.

## Dates

All dates MUST be stored in the ISO 8601 format. Any dates provided in any values MUST match this format.

### Objects and IDs

Users, conferences, channels and messages are objects.

Every object MUST have a numerical ID, which allows it to be quickly located and accessed. These numerical IDs MUST begin at the value of 0, and increase upon every registered object. Object IDs MUST NOT overlap. You **cannot** change an object's ID once it's been assigned.

Information about IDs can be accessed through

```url
/api/v1/id/<ID>
```

In the Euphony Project, the main hierarchy of objects is as follows (from largest/most important to smallest/least important):

* Instance (running a Euphony Project compatible server) - this MUST have the numerical ID of 0
* User (somebody who uses the service)
* Role (groups together certain people in a conference)
* Conference (a group containing channels, compare to Discord's servers/guilds)
* Channel (which contains messages, compare to IRC/Matrix channels or channels in a Discord server/guild)
* Attachment (as in, a quote, poll or other kind of embed)
* Message

Each object, when retrieved, MUST contain the following values in the request returned by the conference alongside its own:

* id (number, contains the object's ID)
* type (string, MUST be object)

where ``<ID>`` is the ID that you want to get information about.

#### Example

An application wants to get information about an user. In order to do so, it must first find its object ID. Once located, this ID can be used to access information about the user, even if they change their name.

### Retrieving information about IDs

In order to get information about an object/action based on its ID, you can query the API:

```url
/api/v1/id/<ID>
```

where ``<ID>`` is the ID you want to get information on. This will return a request that will look as follows:

```json
{
  "id": 1,
  "...": "...insert any required values..."
}
```

where 1 is the ID you requested.

In order to prevent abuse, ALL IDS except for 0 MUST NOT be accessible without prior authentication.

## Federation

Each instance MUST have a public inbox (which can be accessed by other servers) and SHOULD have a private outbox (where requests that will be sent to other instances are stashed).

Federation works on the following principle:

Each channel can be subscribed to, which means that the remote instance knows that it has to send data to another. Instances stash content that has to be sent to other instances' inboxes in a private outbox.

The public inbox is located at

```url
/api/v1/federation/inbox
```

and, upon being queried with a GET request, it MUST return information about the instance (ID 0).

To send an ID to another server, the ID's content is simply POSTed to the remote instance's inbox.

When an object gets from the remote instance to the local instance, the local instance assigns it its own ID, and makes it a regular object. The remote ID and domain are kept in the ``remote-domain`` and ``remote-id`` values.

An example of an ID that was recieved from another instance:

```json
{
  "id": 1,
  "remote-domain": "$remotedomain",
  "remote-id": "remoteid",
  "type": "object",
  "...": "...insert any required values..."
}
```

### Example

U1 wants to join a conference. U1 is on I1, while the conference is on I2. I1 isn't subscribed to the conference yet, so it sends a request to I2 asking to be subscribed to the server. If I2 doesn't block I1 and I2 is up, I1 will subscribe to the conference on I2, thus allowing U1 to communicate with people in the conference.

### Stashing

When the remote server can't be contacted, the local server creates a stash list, which contains the ID ranges that have to be sent to the remote server. It pings the remote server every X minutes (reccomended default: 10 minutes) and if it gets a connection, it sends it the stashed requests. If a server is down for more than 7 days, it is considered closed, until any request is recieved back.

In order to ease this process, servers can send a request to another letting them know that they're back online. This triggers an automatic sync that recieves all requests from a stash without having to wait until the remote server is available. It is reccomended that server software checks for connection dropouts and, once identified, waits for the dropout to end, then send the resync request once the connection is available.

As such, this concept covers two cases:

* one of the servers drops the connection temporarily, but is still running
* one of the servers is shut down

> :warning: Don't send IDs to the remote server that aren't supposed to go it! It's a waste of bandwith and a potential security threat, as bad actors may attempt to intercept information that way.

### Requesting resources from another instance

Since REST API endpoints require authentication, servers must request access to information through the following endpoint on the remote server:

```url
/api/v1/federation/request/...
```

where ``...`` is the same as any API call you would usually make, without the ``/api/v1/`` prefix.

For example, to request an account by name, you would use:

```url
/api/v1/federation/request/account/by-name/U1
```

The remote server will then proceed to send the requested information to the local server's inbox, instead of returning it directly.

### Accessing information about remote instances

When an instance begins to federate with another instance, its ID 0 is copied to

```url
/api/v1/federation/$remotedomain
```

where ``$remotedomain`` is the remote instance's domain.

If queried, this will return the equivalent of the remote server's ID 0 (which contains information about the instance).

``GET $domain/api/v1/federation/$remotedomain``

```json
{
  "id": 0,
  "type": "object",
  "object-type": "instance",
  "...": "...insert instance-specific information here..."
}
```

Assuming an object/action has federated to the instance, it is possible to retrieve its ID on the server it has federated to using

```url
/api/v1/federation/$remotedomain/ID
```

Where ``ID`` is the ID from the remote domain.

This will automatically locate the right ID and print required information.

``GET $domain/api/v1/federation/$remotedomain/$ID``

```json
{
  "remote-domain": "Domain from which the ID was recieved",
  "remote-id": "ID on remote server (number)",
  "id": "ID on local server",
  "...": "...insert other object/action specific information..."
}
```

## Conferences

A conference is a group comprising of any amount of text and voice channels. Users can join a conference, and roles can be given to them. These roles can have certain permissions assigned to them.

### Users

When an user joins a conference and they aren't banned, their ID is added to the conference's user list and they have their conference permission set to 1. Each user can then have additional information assigned to their account:

* their conference-specific nickname;
* the roles they're part of;
* the permissions they have been assigned;
* their ban state (banned or not).

#### Banning

An user can be banned from a conference. This means they cannot join or access the conference.

If an user was banned, their ID can still be queried through ``/api/v1/conference/users/ID``, but only contains the following information:

* "banned?" - bool, true
* "permissions" with the conference bit set to 0

## Channels

Channels are channels of communication that can be nested within conferences or stay standalone as group DMs. There are three types of channels: text channels, media channels (voice and video chat) and direct message channels.

Channels have the ``object-type`` of ``channel``.

### Channel types

#### Text channels

Text channels have the ``channel-type`` of ``text``. They are capable of storing messages.

Text channels MUST be attached to a conference. The conference the channel is placed in is stored in the ``parent-conference`` value.

#### Media channels

Media channels have the ``channel-type`` of ``media``. They are used for transport of voice and video. They MUST be attached to a conference. The conference the channel is placed in is stored in the ``parent-conference`` value.

> TODO: How is audio and video going to be transported? Do some research on this.

#### Direct message channels

Direct message channels can transport both text and media. They have the same API calls as both text and media channels. They have the ``channel-type`` of ``direct-message``.

Direct message channels MUST NOT be attached to a conference. The ``parent-conference`` MUST be ignored when paired with direct message channels.

#### Categories

Categories have the ``channel-type`` of ``category``. They can group together text and media channels in a conference.

Categories MUST be attached to a conference. The conference the channel is placed in is stored in the ``parent-conference`` value.

### Messages

Text channels and direct message channels can store messages. These messages can then be retrieved in two ways: by post date and by ID.

```url
/api/v1/channel/messages/{by-date/by-id}/{date/ID}
```

## Attachments

Attachments are objects that can be attached to a message for additional information. The following attachement types are available:

### Quote

```json
{
  "attachment-type": "quote",
  "quoted-message": "id"
}
```

Adds a quote to a message. Should be displayed before the message. Can be used as a reply function.

### Media

```json
{
  "attachment-type": "media",
  "media-link": "https://link-to-media/image.png"
}
```

Adds media to the message. Should be displayed after the message.

Media is one of the following:

- an image (in which case, it SHOULD be embedded as such)
- a video (in which case, it SHOULD be embedded as such)
- a sound file (in which case, it SHOULD be embedded as such)
- any other file

Any image, video or sound links SHOULD be interpreted as an attachement and embedded accordingly.

## Permissions

Permissions are stored in a single string value using numbers, where each number represents a permission set. This value is called a permission map and has the following layout:

``"permissions": 12345``

* 1 - message
* 2 - channel
* 3 - conference
* 4 - roles
* 5 - user

Permissions can be assigned to a conference, a channel, a role or an user in a conference. The order in which permissions are read and overwritten is as follows (from the least to the most important):

* conference
* channel
* role
* user in a conference

The RECCOMENDED initial permission map for an user in a conference is ``21101``.

Permission maps MUST be stored in strings, in order to prevent trailing ``0``s from being cut.

### List of permission sets

#### Message

* 0 - cannot read or write
* 1 - can read
* 2 - can read and write
* 3 - can pin or delete other user's messages

#### Channel

* 0 - cannot see channel
* 1 - can see channel, but can't read/write from/to it
* 2 - can read and write in the channel
* 3 - can modify channels

#### Conference

* 0 - cannot access the conference (user banned or conference pasword-locked and no/wrong password provided)
* 1 - can access the conference
* 2 - can modify the conference

#### Role

* 0 - cannot modify or assign roles
* 1 - can modify or assign roles

#### User

* 0 - cannot modify nicknames of, kick or ban users
* 1 - can change their own nickname but can't modify other users
* 2 - can modify other users' and their own nicknames
* 3 - can modify other users' and their own nicknames and kick
* 4 - can modify other users' and their own nicknames, kick and ban

## Messages

Messages are single messages in a text channel. They MUST be attached to a text channel, the ID of which is stored in the ``channel-id`` value.

___

## List of valid REST API calls

This section contains evert REST API call that can be made, alongside a description and expected output.

This section is intended for developement purposes only; most of the calls are properly explained above. This list is to be used as a referrence for possible implementations.

### GET /api/v1/instance

Returns ID 0 (information about the instance).

See details about the Instance object in the List of objects with properties for more information.

### GET /api/v1/id/$ID

Returns information about the object associated with the ID. If the ID does not exist, it MUST return the 404 status code.

This request MUST require authentication, unless ID 0 is being queried.

Please note that this request does not, and MUST NOT, allow for operations on the ID (such as pushing or patching).

### GET /api/v1/id/$ID/type

Returns the type and object-type of an ID. If the ID does not exist, it MUST return the 404 status code.

This request MUST require authentication, unless ID 0 is being queried.

### GET /api/v1/accounts/$ID

Returns information about an account, by ID. If the ID is not an account, it MUST return:

```json
{
  "error": "Not an account"
}
```

If the ID does not exist, it MUST return the 404 status code.

This returns an Account object. See details about the Account object in the List of objects with properties for more information.

#### Example output

```json
{
  "id": 1,
  "type": "object",
  "object-type": "account",
  "nickname": "example",
  "bio": "Test account",
  "status": "Testing :)",
  "email": "tester@example.com"
}
```

### PATCH /api/v1/accounts/$ID

Modifies information about an account.

### GET /api/v1/accounts/by-name/$NAME

Returns information about an account, by name. The name MUST be the name of a local user, without the trailing ``@`` and the ``@domain`` suffix.

This can only be used with accounts registered on the server.

If there is no account with such name, it MUST return the 404 status code.

This returns an Account object. See details about the Account object in the List of objects with properties for more information.

### PATCH /api/v1/accounts/by-name/$NAME

Modifies information about an account, by name.

### GET /api/v1/messages/by-id/$ID

Returns information about a message, by ID. If the ID does not belong to a message, it MUST return:

```json
{
  "error": "Not a message"
}
```

If the ID does not exist, it MUST return the 404 status code.

#### Example output

```json
{
  "id": 4,
  "type": "object",
  "object-type": "message",
  "channel-id": "3",
  "creator": "1",
  "post-date": "0",
  "content": "Testing messages."
}
```

### GET /api/v1/messages/by-time/$MINUTES

Get all messages from X minutes ago. Returns a list of IDs.

#### Example output

```json
{
    "messages": [ 1, 2, 3 ]
}
```

### GET /api/v1/messages/by-date/YYYY-MM-DD

Get all messages posted since a certain date. Returns a list of IDs, simmilarily to ``/api/v1/messages/by-time``.

### POST /api/v1/messages

Takes a Message object and posts it to the specified channel (specified in the ``channel-id`` value). Returns the ``id`` of the resulting message.

### PATCH /api/v1/messages

Takes a Message object with the ``id`` value set to the message that will be edited. Server-side, this should change the ``edit-date`` variable to the time of edition and the ``edited?`` bool to true.

### POST /api/v1/federation/inbox

Federation inbox. See the Federation section. MUST NOT be GETable.

### GET /api/v1/conference/ID

Returns a Conference object, by ID. If the ID does not belong to a conference, it MUST return:

```json
{
  "error": "Not a conference"
}
```

If the ID does not exist, it MUST return the 404 status code.

### POST /api/v1/conference

Takes a Conference object and creates it. Returns the ID of the resulting conference.

### GET /api/v1/conference/user/ID

Returns information about the user's nickname, roles and permissions. See the Conferences > Users section for more information.

If the ID does not belong to an account, it MUST return the 404 status code.

If the user does not belong to the conference, it MUST return the 404 status code.

If the ID does not exist, it MUST return the 404 status code.

### PATCH /api/v1/conference/user/ID

Modifies information about an user in a conference.

## List of objects with properties

This section contains every object with its required values.

> :information_source: The layout of each property is as follows:
> name (type, optional description) {read/write permissions (read - r, write - w)}

### Instance

``"object-type": "instance"``

| Key             | Value type | Required? | Require authentication?         | Read/write | Federate? | Notes                                                                                 |
|-----------------|------------|-----------|---------------------------------|------------|-----------|---------------------------------------------------------------------------------------|
| address         | string     | yes       | r: no; w: no                    | r          | yes       | Contains the domain name for the instance. Required for federation.  MUST NOT CHANGE. |
| server-software | string     | yes       | r: no; w: no                    | r          | yes       | Contains the name and version of the used server software.                            |
| name            | string     | yes       | r: no; w: yes [instance:modify] | r[w]       | yes       | Contains the name of the server. This can be changed by an user.                      |
| description     | string     | yes       | r: no; w: yes [instance:modify] | r[w]       | yes       | Contains the description of the server. This can be changed by an user.               |

### Account

``"object-type": "account"``

| Key             | Value type | Required? | Require authentication?         | Read/write | Federate? | Notes                                                                                 |
|-----------------|------------|-----------|---------------------------------|------------|-----------|---------------------------------------------------------------------------------------|
| username        | string     | yes       | r: no; w: yes [account:modify]  | rw         | yes       | Instancewide username. There MUST NOT be two users with the same username.            |
| status          | string     | no        | r: no; w: yes [account:modify]  | rw         | yes       | User status.                                                                          |
| bio             | string     | no        | r: no; w: yes [account:modify]  | rw         | yes       | User bio. Hashtags can be taken as profile tags and used in search engines.           |
| index?          | bool       | yes       | r: no; w: yes [account:modify]  | rw         | yes       | Can the user be indexed in search results? MUST be ``no`` by default.                 |
| email           | string     | yes       | r: yes; w: yes [account:modify] | rw         | no        | User email. Used for logging in.                                                      |

### Channel

``"object-type": "channel"``

| Key             | Value type | Required? | Require authentication?             | Read/write | Federate? | Notes                                                                                 |
|-----------------|------------|-----------|-------------------------------------|------------|-----------|---------------------------------------------------------------------------------------|
| name            | string     | yes       | r: yes*; w: yes [x3xxx permissions] | rw         | yes       | Contains the name of the channel. If the channel is a direct message channel with one participant, the name is set to the IDs of the users in the conversations, separated by a space.|
| description     | string     | no        | r: yes*; w: yes [x3xxx permissions] | rw         | yes       | Contains the name and version of the used server software.                            |
| perimssions     | string     | yes       | r: yes*; w: yes [x3xxx permissions] | rw         | yes       | Contains the permissions for the channel. This is a permission map.                   |

``* Must require prior per-user authentication. Direct message channels require the user to be a part of the direct message. Channels in conferences require the user to join the conference.``

#### Direct message channels

Beside the regular channel values, direct message channels have the following additional values:

| Key             | Value type      | Required? | Require authentication?                              | Read/write | Federate? | Notes                                                                                       |
|-----------------|-----------------|-----------|------------------------------------------------------|------------|-----------|---------------------------------------------------------------------------------------------|
| members         | list of numbers | yes       | r: yes* (can't write, this is handled by the server) | r          | yes       | Contains the IDs of the members of the direct message.                                      |
| icon            | string          | yes       | r: yes* w: yes [x3xxx permissions]                   | rw         | yes       | Contains the icon of the direct message. This is a link. Servers MUST provide placeholders. |

``* Must require prior per-user authentication.``

### Message

``"object-type": "message"``

| Key             | Value type | Required? | Require authentication?                                                 | Read/write | Federate? | Notes                                                                              |
|-----------------|------------|-----------|-------------------------------------------------------------------------|------------|-----------|------------------------------------------------------------------------------------|
| content         | string     | yes       | r: no; w: yes [must be authenticated as the user who wrote the message] | rw         | yes       | Message content. Any further writes are counted as edits.                          |
| attachment      | number     | no        | r: no; w: yes [must be authenticated as the user who wrote the message] | rw         | yes       | ID of the attachment. Any further writes are counted as edits.                     |
| parent-channel  | number     | yes       | r: no                                                                   | r          | yes       | ID of the channel in which the message has been posted. Assigned by the server at message creation. |
| author          | number     | yes       | r: no                                                                   | r          | yes       | ID of the message author. Assigned by the server at message creation.              |
| post-date       | string     | yes       | r: no                                                                   | r          | yes       | Date of message creation. Assigned by the server at message creation.              |
| edit-date       | string     | no        | r: no                                                                   | r          | yes       | Date of last message edit. Assigned by the server at message edit.                 |
| edited?         | bool       | yes       | r: no                                                                   | r          | yes       | Is the message edited? Defaults to ``false``. Set by the server at message edit.   |

### Conference

``"object-type": "conference"``

| Key           | Value type      | Required? | Require authentication?           | Read/write | Federate? | Notes                                                                                          |
|---------------|-----------------|-----------|-----------------------------------|------------|-----------|------------------------------------------------------------------------------------------------|
| name          | string          | yes       | r: no; w: yes [xx3xx permissions] | rw         | yes       | Name of the conference.                                                                        |
| description   | string          | yes       | r: no; w: yes [xx3xx permissions] | rw         | yes       | Description of the conference.                                                                 |
| icon          | string          | yes       | r: no; w: yes [xx3xx permissions] | rw         | yes       | URL of the conference's icon. Servers MUST provide a placeholder.                              |
| owner         | number          | yes       | r: no; w: yes [user needs to be authenticated and be the owner of the conference] | rw | yes | ID of the conference's owner. MUST be an account. Initially assigned at conference creation by the server. |
| index?        | bool            | yes       | r: no; w: yes [user needs to be owner] | rw    | yes       | Should the conference be indexed in search results? SHOULD default to ``false``.               |
| permissions   | string          | yes       | r: no; w: yes [xx3xx permissions] | rw         | yes       | Conference-wide permission set, stored as a permission map.                                    |
| creation-date | string          | yes       | r: no                             | r          | yes       | Date of the conference's creation. Assigned by the server.                                     |
| channels      | list of numbers | yes       | r: no                             | r          | yes       | List of IDs of channels present in the conference. Assigned by the server at channel creation. |
| users         | list of numbers | yes       | r: yes [user needs to be authenticated and in the conference] | r | yes | List of IDs of users who have joined the conference. Modified by the server when an user joins. |
| roles         | list of numbers | no        | r: yes [xxx1x permissions]        | r          | yes       | List of IDs of roles present in the conference. Modified by the server when a role is added.   |

### Role

``"object-type": "role"``

| Key           | Value type | Required? | Require authentication?           | Read/write | Federate? | Notes                                                                                           |
|---------------|------------|-----------|-----------------------------------|------------|-----------|-------------------------------------------------------------------------------------------------|
| name          | string     | yes       | r: no; w: yes [xxx1x permissions] | rw         | yes       | Name of the role.                                                                               |
| description   | string     | no        | r: no; w: yes [xxx1x permissions] | rw         | yes       | Short description of the role.                                                                  |
| color         | string     | yes       | r: no; w: yes [xxx1x permissions] | rw         | yes       | Color of the role, in RGB ("R, G, B" (does not support alpha)). Servers MUST provide a default. |
| permissions   | string     | no        | r: no; w: yes [xxx1x permissions] | rw         | yes       | Permissions for the role, as a permission map.                                                  |

### Attachment

``"object-type": "attachment"``

| Key             | Value type      | Required? | Require authentication?                        | Read/write          | Federate? | Notes                                         |
|-----------------|-----------------|-----------|------------------------------------------------|---------------------|-----------|-----------------------------------------------|
| attachment-type | string          | yes       | r: no; w: yes [user needs to be authenticated] | rw (not rewritable) | yes       | Attachment type. See the Attachments section. |

#### Quote

``"attachment-type": "quote"``

| Key            | Value type | Required? | Require authentication?                        | Read/write | Federate? | Notes                     |
|----------------|------------|-----------|------------------------------------------------|------------|-----------|---------------------------|
| quoted-message | number     | yes       | r: no; w: yes [user needs to be authenticated] | rw         | yes       | ID of the quoted message. |

#### Media

``"attachment-type": "media"``

| Key        | Value type | Required? | Require authentication?                        | Read/write | Federate? | Notes                      |
|------------|------------|-----------|------------------------------------------------|------------|-----------|----------------------------|
| media-link | string     | yes       | r: no; w: yes [user needs to be authenticated] | rw         | yes       | URL of the attached media. |

