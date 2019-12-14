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

All dates MUST be stored as time from the UNIX epoch. This prevents date formatting issues and makes them easier to parse.

### Objects and IDs

Users, servers, channels and messages are objects. 

Every object MUST have a numerical ID, which allows it to be quickly located and accessed. These numerical IDs MUST begin at the value of 0, and increase upon every registered object. Object IDs MUST NOT overlap. You **cannot** change an object's ID once it's been assigned.

Information about IDs can be accessed through

```url
/api/v1/id/<ID>
```

In the Euphony Project, the main hierarchy of objects is as follows (from largest/most important to smallest/least important):

* Instance (running a Euphony Project compatible server) - this MUST have the numerical ID of 0
* User (somebody who uses the service)
* Role (servers together certain people in a server)
* Server (a group containing channels, compare to Discord's servers/guilds)
* Channel (which contains messages, compare to IRC/Matrix channels or channels in a Discord server/guild)
* Attachement (as in, a quote, poll or other kind of embed)
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

U1 wants to join a server. U1 is on I1, while the server is on I2. I1 isn't subscribed to the server yet, so it sends a request to I2 asking to be subscribed to the server. If I2 doesn't block I1 and I2 is up, I1 will subscribe to the server on I2, thus allowing U1 to communicate with people on the server.

U2 is on I2. U2 sends a message to the server on I2. The server pings every subscribed instance, including I2, sending them the action. I1 gets the action, saves it on itself and sends a confirmation to the server.

### Stashing

When the remote server can't be contacted, the local server creates a stash list, which contains the ID ranges that have to be sent to the remote server. It pings the remote server every X minutes (reccomended default: 10 minutes) and if it gets a connection, it sends it the stashed requests. If a server is down for more than 7 days, it is considered closed, until any request is recieved back.

In order to ease this process, servers can send a request to another letting them know that they're back online. This triggers an automatic sync that recieves all requests from a stash without having to wait until the remote server is available. It is reccomended that server software checks for connection dropouts and, once identified, waits for the dropout to end, then send the resync request once the connection is available.

As such, this concept covers two cases:

* one of the servers drops the connection temporarily, but is still running
* one of the servers is shut down

> :warning: Don't send IDs to the remote server that aren't supposed to go it! It's a waste of bandwith and a potential security threat, as bad actors may attempt to intercept information that way.

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

## Servers

> :warning: DO NOT confuse servers with instances or group DMs!

A server is a group comprising of any amount of text and voice channels. Users can join a server, and roles can be given to them. These roles can have certain permissions assigned to them.

## Channels

Channels are channels of communication that can be nested within servers or stay standalone as group DMs. There are three types of channels: text channels, media channels (voice and video chat) and direct message channels.

Channels have the ``object-type`` of ``channel``.

### Text channels

Text channels have the ``channel-type`` of ``text``. They are capable of storing messages. 

Text channels MUST be attached to a server. The server the channel is placed in is stored in the ``parent-server`` value.

### Media channels

Media channels have the ``channel-type`` of ``media``. They are used for transport of voice and video. They MUST be attached to a server. The server the channel is placed in is stored in the ``parent-server`` value.

> TODO: How is audio and video going to be transported? Do some research on this.

### Direct message channels

Direct message channels can transport both text and media. They have the same API calls as both text and media channels. They have the ``channel-type`` of ``direct-message``.

Direct message channels MUST NOT be attached to a server. The ``parent-server`` MUST be ignored when paired with direct message channels.

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

### GET /api/v1/messages/$ID

Returns information about a message, by ID. If the ID does not belong to a message, it MUST return:

```json
{
  "error": "Not an account"
}
```

If the ID does not exist, it MUST return the 404 status code.

#### Example output

```json
{
  "id": 4,
  "type": "object",
  "object-type": "message",
  "server-id": "3",
  "creator": "1",
  "post-date": "0",
  "content": "Testing messages."
}
```

### POST /api/v1/messages

Takes a Message object and posts it to the server.

## List of objects with properties

This section contains every object with its required values.

> :information_source: The layout of each property is as follows:
> name (type, optional description) {read/write permissions (read - r, write - w)}

### Instance

``"object-type": "instance"``

| Key             | Value type | Required? | Require authentication? | Read/write | Federate? | Notes                                                                                 |
|-----------------|------------|-----------|---------------------------------|------------|-----------|---------------------------------------------------------------------------------------|
| address         | string     | yes       | r: no; w: no                    | r          | yes       | Contains the domain name for the instance. Required for federation.  MUST NOT CHANGE. |
| server-software | string     | yes       | r: no; w: no                    | r          | yes       | Contains the name and version of the used server software.                            |
| name            | string     | yes       | r: no; w: yes [instance:modify] | r[w]       | yes       | Contains the name of the server. This can be changed by an user.                      |
| description     | string     | yes       | r: no; w: yes [instance:modify] | r[w]       | yes       | Contains the description of the server. This can be changed by an user.               |

### Account

``"object-type": "account"``


- object-type (string, MUST be "account")
- nickname (string) {r[w]} [account.modify]
- status (string) {r[w]} [account.modify]
- bio (string) {r[w]} [account.modify]

#### Private values (require scope for reading)

- email (string, DO NOT FEDERATE) {[rw]} [account.modify]

### Channel

### Message

#### Public values

- object-type (string, MUST be "message")
- content (string) {r[w]} [message.edit]
- channel-id (number, contains ID of the channel) {r}
- creator (number, contains ID of the account who sent the message) {r}
- post-date (number, date) {r}
- edit-dates (list with numbers, date, optional) {r}
- attachement (string, contains link to file with https:// or http:// prefix) {r}

### Server

#### Public values

- object-type (string, MUST be "server")
- name (string)
- description (string)
- creation-date (number, date)
- channels (list of numbers, contains IDs for text and voice channels on the server)
- users (list of numbers, contains IDs of users on the server)

#### Private values (require scope)

##### Settings

**Information** [server:info]

- name (string) {r[w]}
- description (string) {r[w]}
- icon (string, link to file with https:// or http:// prefix) {r[w]}
- in-search-index (bool, decides if the server can be found through built-in search tools. The reccomended default is false.) {r[w]}
- owner (number, ID of owner user) {r, rw with server.changeowner scope}

**Roles** [server:roles]

> :information_source: Note: this scope is also required to view information about individual roles.

- roles (list of numbers, contains IDs of roles on the server)

**Individual role information** (``$domain/api/v1/server/role/ID``)

- object-type (string, MUST be "role")
- name (string) {r[w]}
- description (string, small description of role) {r[w]}
- permissions (list - permission map (see Permissions for more information))

#### Closed values (cannot be requested)

- password (contains server password if one is set)
